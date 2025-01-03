import eventlet

eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room
from urllib.parse import urljoin

from typing import *
import argparse

import os
import sys

import logging
logging.basicConfig(level=logging.INFO)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.dont_write_bytecode = True

from server.controller import Controller, UsersManager

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, async_model='eventlet')
users_manager = UsersManager()
controller: Optional[Controller] = None

audio_server_url = ""


@socketio.on("connect")
def handle_connect():
    user_id = users_manager.allocate(request.sid)
    socketio.emit("user_id", {"user_id": user_id}, to=request.sid)
    app.logger.info(f"Client connected. {request.sid} {user_id}")
    

@socketio.on("disconnect")
def handle_disconnect():
    user_id = users_manager.deallocate(request.sid)
    app.logger.info(f"Client disconnected. {request.sid} {user_id}")


@socketio.on("join")
def handle_join(room):
    join_room(room)
    app.logger.info(f'Client joins room "{room}". {request.sid}')


@socketio.on("uplink_message")
def handle_uplink_message(message):
    app.logger.info(f"Received uplink_message: {message}")
    controller.put_uplink_message(Controller.parse_uplink_message(message))


@app.route("/")
def index():
    return render_template("test.html", audio_server_url=audio_server_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="Port number")
    parser.add_argument("db", type=str, help="Database path")
    parser.add_argument("music", type=str, help="Music path")
    parser.add_argument(
        "audio_server_url",
        type=str,
        help="Audio Server URL (e.g. http://0.0.0.0:5000)",
    )
    parser.add_argument("--keyfile", type=str, help="Path to the SSL key file")
    parser.add_argument("--certfile", type=str, help="Path to the SSL certificate file")
    args = parser.parse_args()

    audio_server_url = args.audio_server_url
    controller = Controller(socketio, users_manager, args.db, args.music, urljoin(args.audio_server_url, "/audio_ctrl"))
    controller.start()

    if args.keyfile and args.certfile:
        socketio.run(app, host="0.0.0.0", port=args.port, certfile=args.certfile, keyfile=args.keyfile)
    else:
        socketio.run(app, host="0.0.0.0", port=args.port)
