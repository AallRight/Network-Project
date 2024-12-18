import asyncio
import logging
from quart import Quart, request, jsonify, send_from_directory
from quart_cors import cors
from aiortc import RTCPeerConnection, RTCSessionDescription
from audioCTRL import AudioController
import json
import uuid
import os

# 创建 Quart 应用
app = Quart(__name__)
app = cors(app, allow_origin="*")

# 设置静态文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.static_folder = os.path.join(BASE_DIR, "static")


# 配置日志
logging.basicConfig(level=logging.INFO)

# 存储多个连接
pcs = {}  # {connection_id: RTCPeerConnection}

# 创建 AudioCTRL 实例
audio_ctrl = AudioController(buffer_capacity=1, sample_rate=48000)


@app.route("/")
async def index():
    # 返回 index.html
    return await send_from_directory(app.static_folder,
                                     "index.html")


@app.route('/<path:filename>')
async def static_files(filename):
    return await send_from_directory(app.static_folder, filename)


@app.before_serving
async def start_audio_ctrl():
    """初始化音频控制器"""
    audio_ctrl.create_play_thread()
    audio_ctrl.create_microphone_thread()

    await audio_ctrl.start_audio_playback()
    await audio_ctrl.load_music_file("K_song/music/时暮的思眷.wav")


@app.route("/offer", methods=["POST"])
async def offer():
    """处理 WebRTC offer 并返回 answer"""
    offer_sdp = (await request.get_json()).get("sdp")

    # 创建新的 RTCPeerConnection 实例
    connection_id = str(uuid.uuid4())
    pc = RTCPeerConnection()
    pcs[connection_id] = pc
    logging.info(f"Connection {connection_id} created")

    @pc.on("track")
    async def on_track(track):
        if track.kind == "audio":
            await audio_ctrl.add_audio_track(connection_id, track)

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type="offer"))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
        "connection_id": connection_id
    })


@app.route("/ice-candidate/<connection_id>", methods=["POST"])
async def ice_candidate(connection_id):
    """处理 ICE candidate"""
    data = await request.get_json()
    candidate = data.get("candidate")
    if connection_id in pcs:
        pc = pcs[connection_id]
        await pc.addIceCandidate(candidate)
        return jsonify({"message": "Candidate added"})
    else:
        return jsonify({"message": "Connection not found"}), 404


@app.route("/close/<connection_id>", methods=["POST"])
async def close_connection(connection_id):
    """关闭指定连接"""
    if connection_id in pcs:
        pc = pcs.pop(connection_id)
        await pc.close()
        logging.info(f"Connection {connection_id} closed")
        return jsonify({"message": "Connection closed"})
    else:
        return jsonify({"message": "Connection not found"}), 404


@app.route("/play_local", methods=["POST"])
async def play_local():
    """播放本地音频"""
    await audio_ctrl.play_music()
    return jsonify({"message": "Local audio playing"})


@app.route("/pause_local", methods=["POST"])
async def pause_local():
    """暂停本地音频播放"""
    await audio_ctrl.pause_music()
    return jsonify({"message": "Local audio stopped"})


@app.route("/adjust_time", methods=["POST"])
async def adjust_time():
    """调整播放时间"""
    time = (await request.get_json()).get("time")
    await audio_ctrl.adjust_playback_time(time)
    return jsonify({"message": "Time adjusted"})


@app.route("/mic_volume", methods=["POST"])
async def mic_volume():
    """调整麦克风音量"""
    volume = (await request.get_json()).get("volume")
    await audio_ctrl.adjust_volume(volume, True)
    return jsonify({"message": "Mic volume adjusted"})


@app.route("/music_volume", methods=["POST"])
async def music_volume():
    """调整音乐音量"""
    volume = (await request.get_json()).get("volume")
    await audio_ctrl.adjust_volume(volume, False)
    return jsonify({"message": "Music volume adjusted"})


@app.route("/open_mic", methods=["POST"])
async def open_mic():
    """打开麦克风"""
    await audio_ctrl.start_microphone_recording()
    return jsonify({"message": "Mic opened"})


@app.route("/close_mic", methods=["POST"])
async def close_mic():
    """关闭麦克风"""
    await audio_ctrl.stop_microphone_recording()
    return jsonify({"message": "Mic closed"})

if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=9000)
    app.run(host="0.0.0.0", port=9000)  # 监听所有公网 IP
