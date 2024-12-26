import logging
from quart import Quart, request, jsonify, send_from_directory
from quart_cors import cors
import json
import os
import websockets

# 创建 Quart 应用
app = Quart(__name__)
app = cors(app, allow_origin="*")

# 设置静态文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.static_folder = os.path.join(BASE_DIR, "static")


@app.route("/")
async def index():
    # 返回 index.html
    return await send_from_directory(app.static_folder,
                                     "index.html")


@app.route('/<path:filename>')
async def static_files(filename):
    return await send_from_directory(app.static_folder, filename)


# * 使用 websocket 和 AudioCTRL 进程间通信
url_ctrl = "ws://localhost:5000/audio_ctrl"


async def send_to_CTRL(message):
    # 连接到音频控制器
    socket_ctrl = await websockets.connect(url_ctrl, origin="http://localhost:9000")
    logging.info("连接到音频控制器")

    await socket_ctrl.send(json.dumps(message))
    logging.info(f"发送到音频控制器: {message}")

    response_string = await socket_ctrl.recv()
    response = json.loads(response_string)
    logging.info(f"收到音频控制器响应: {response}")

    await socket_ctrl.close()
    logging.info("与音频控制器断开连接")

    return response


@app.before_serving
async def initial_device():
    """初始化进程间通信"""
    await send_to_CTRL({"function": "测试连接：初始化音频控制器"})


@app.route("/play_local", methods=["POST"])
async def play_local():
    """播放本地音频"""
    await send_to_CTRL({"function": "play_music"})
    return jsonify({"message": "Local audio playing"})


@app.route("/pause_local", methods=["POST"])
async def pause_local():
    """暂停本地音频播放"""
    await send_to_CTRL({"function": "pause_music"})
    return jsonify({"message": "Local audio stopped"})


@app.route("/adjust_time", methods=["POST"])
async def adjust_time():
    """调整播放时间"""
    time = (await request.get_json()).get("time")
    await send_to_CTRL({"function": "adjust_playback_time", "time": time})
    return jsonify({"message": "Time adjusted"})


@app.route("/mic_volume", methods=["POST"])
async def mic_volume():
    """调整麦克风音量"""
    volume = (await request.get_json()).get("volume")
    await send_to_CTRL({"function": "adjust_volume", "volume_delta": volume, "is_mic": True})
    return jsonify({"message": "Mic volume adjusted"})


@app.route("/music_volume", methods=["POST"])
async def music_volume():
    """调整音乐音量"""
    volume = (await request.get_json()).get("volume")
    await send_to_CTRL({"function": "adjust_volume", "volume_delta": volume, "is_mic": False})
    return jsonify({"message": "Music volume adjusted"})


@app.route("/open_mic", methods=["POST"])
async def open_mic():
    """打开麦克风"""
    await send_to_CTRL({"function": "start_microphone_recording"})
    return jsonify({"message": "Mic opened"})


@app.route("/close_mic", methods=["POST"])
async def close_mic():
    """关闭麦克风"""
    await send_to_CTRL({"function": "stop_microphone_recording"})
    return jsonify({"message": "Mic closed"})

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=9000)  # 监听本地 IP
    # app.run(host="0.0.0.0", port=9000)  # 监听所有公网 IP
