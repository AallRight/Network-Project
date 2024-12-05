from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room
import threading
from typing import *
import argparse
import queue
import threading
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.dont_write_bytecode = True

from server.controller import Controller, UsersManager, ESCAPE_USER_ID

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
controller: Optional[Controller] = None
users_manager = UsersManager()
uplink_message_queue = queue.Queue()

@socketio.on('connect')
def handle_connect():
    user_id = users_manager.allocate(request.sid)
    socketio.emit('user_id', {'user_id': user_id}, to=request.sid)
    app.logger.info(f'Client connected. {request.sid} {user_id}')

@socketio.on('disconnect')
def handle_disconnect():
    user_id = users_manager.deallocate(request.sid)
    app.logger.info(f'Client disconnected. {request.sid} {user_id}')

@socketio.on('join')
def handle_join(room):
    join_room(room)
    app.logger.info(f'Client joins room "{room}". {request.sid}')

@socketio.on('uplink_message')
def handle_uplink_message(message):
    app.logger.info(f'Received uplink_message: {message}')
    uplink_message_queue.put(message)

@app.route('/')
def index():
    return render_template('test.html')

def process_uplink_message():
    while True:
        uplink_message = uplink_message_queue.get()
        downlink_message, to_user_id = controller.handle(uplink_message)
        if to_user_id is None:
            socketio.emit('downlink_message', downlink_message)  # broadcast
        else:
            sid = users_manager.get_sid(to_user_id)
            if sid is not None:
                socketio.emit('downlink_message', downlink_message, to=sid)
            elif to_user_id != ESCAPE_USER_ID:
                app.logger.error(f"user_id {to_user_id} not found!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="Port number")
    parser.add_argument("db", type=str, help="Database path")
    parser.add_argument("music", type=str, help="Music path")
    args = parser.parse_args()

    controller = Controller(args.db, args.music)
    threading.Thread(target=process_uplink_message, daemon=True).start()

    socketio.run(app, host='0.0.0.0', port=args.port)
