from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room
from redis import Redis
from redis import RedisError
import threading
import json
import argparse

from model import Model
from media import Player

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
redis = Redis()
db = Model()
player = Player()


def listen_to_redis():
    pubsub = redis.pubsub()
    pubsub.subscribe('changes')
    
    for response in pubsub.listen():
        if response['type'] == 'message':
            # 3. Process
            manipulation = json.loads(response['data'].decode('utf-8'))
            applied_changes = db.manipulate(
                change=manipulation['change'], 
                based_on_version=manipulation['based_on_version'])
            # 4. Broadcast
            for based_on_version, change in applied_changes.items():
                broadcast_msg = json.dumps({'change': change, 'based_on_version': based_on_version})
                socketio.emit('change', broadcast_msg, to="clients")

@app.route('/')
def index():
    return render_template('client.html')

@app.route('/player')
def get_player_page():
    return render_template('player.html')

@app.route('/model', methods=['GET'])
def get_model():
    serialized_db = db.serialize()
    return serialized_db

@socketio.on('connect')
def handle_connect():
    print(f'Client connected. SID: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected.')

@socketio.on('join')
def handle_join(room):
    join_room(room)
    print(f'Client joins room "{room}". SID: {request.sid}')

@socketio.on('change')
def handle_change(change):
    print(f'Received change: {change}')
    # 2. queue
    redis.publish('changes', change)

@socketio.on('media')
def handle_media(audio):
    # print(f'Received media: {len(audio)} {type(audio)}')
    # socketio.emit('media', audio, to="players")
    player.write(audio)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="Port number")
    args = parser.parse_args()

    threading.Thread(target=listen_to_redis, daemon=True).start()
    player.start()

    socketio.run(app, host='0.0.0.0', port=args.port)

    player.stop()