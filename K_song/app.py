from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求

# 加载数据
with open('data/song_queue.json', 'r') as f:
    song_queue = json.load(f)

with open('data/song_data.json', 'r') as f:
    song_data = json.load(f)


# 路由定义
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/song_data', methods=['GET'])
def get_song_data():
    return jsonify(song_data)


@app.route('/song_data/<int:song_id>', methods=['GET'])
def get_specific_song(song_id):
    song = next((s for s in song_data if s['data_id'] == song_id), None)
    if song:
        return jsonify(song)
    return jsonify({"error": "Song not found"}), 404


@app.route('/song_queue', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_song_queue():
    if request.method == 'GET':
        return jsonify(song_queue)

    elif request.method == 'POST':
        new_song = request.json

        new_song['queue_id'] = len(song_queue)
        song_queue.append(new_song)

        return jsonify({"message": "Song added successfully", "song_queue": song_queue})

    elif request.method == 'PUT':
        action = request.json.get('action')
        index = request.json.get('queue_id')

        if index is None:
            return jsonify({"message": "Song not found"}), 404

        if action == "MOVE_UP" and index > 0:
            song_queue[index], song_queue[index -
                                          1] = song_queue[index - 1], song_queue[index]
            song_queue[index]['queue_id'] = index
            song_queue[index - 1]['queue_id'] = index - 1

            return jsonify({"message": "Song moved up", "song_queue": song_queue})

        elif action == "MOVE_DOWN" and index < len(song_queue) - 1:
            song_queue[index], song_queue[index +
                                          1] = song_queue[index + 1], song_queue[index]
            song_queue[index]['queue_id'] = index
            song_queue[index + 1]['queue_id'] = index + 1

            return jsonify({"message": "Song moved down", "song_queue": song_queue})

        elif action == "MOVE_FIRST" and index > 0:
            song = song_queue.pop(index)
            song_queue.insert(0, song)
            for i, song in enumerate(song_queue):
                song['queue_id'] = i

            return jsonify({"message": "Song moved to first", "song_queue": song_queue})
        else:

            return jsonify({"song_queue": song_queue})

    elif request.method == 'DELETE':

        index = request.json.get('queue_id')
        print(index)

        if index is None:
            return jsonify({"message": "Song not found"}), 404

        song_queue.pop(index)

        for i, song in enumerate(song_queue):
            song['queue_id'] = i

        return jsonify({"message": "Song removed", "song_queue": song_queue})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
