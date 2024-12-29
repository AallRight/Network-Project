import logging
from quart import Quart, request, jsonify, websocket, send_from_directory
from quart_cors import cors
from aiortc import RTCPeerConnection, RTCSessionDescription
from audioCTRL import AudioController
import json
import uuid
import os

# 创建 Quart 应用
app = Quart(__name__)
app = cors(app, allow_origin="*", allow_methods="*", allow_headers="*")

# 配置日志
logging.basicConfig(level=logging.INFO)

# 存储多个连接
pcs = {}  # {connection_id: RTCPeerConnection}


# 创建音频控制器实例
audio_ctrl = AudioController(buffer_capacity=5,
                             sample_rate=48000,
                             process_interval=0.001,
                             chunk_size=1920)


# 设置静态文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.static_folder = os.path.join(BASE_DIR, "static")

# 配置日志
logging.basicConfig(level=logging.INFO)


@app.route("/")
async def index():
    # 返回 index.html
    return await send_from_directory(app.static_folder,
                                     "index.html")


@app.route('/<path:filename>')
async def static_files(filename):
    return await send_from_directory(app.static_folder, filename)


@app.before_serving
async def initial_device():
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
            logging.info(f"Audio track added to connection {connection_id}")

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


# 音频控制器 WebSocket 通信
@app.websocket("/audio_ctrl")
async def websocket_handler():

    # 接收客户端消息
    json_string = await websocket.receive()
    message = json.loads(json_string)
    logging.info(f"收到客户端消息: {message}")

    # 处理客户端消息
    if message["function"] == "load_music_file":
        await audio_ctrl.load_music_file(message["file_path"])
        await websocket.send(json.dumps({"response": "音乐文件已加载"}))

    if message["function"] == "play_music":
        await audio_ctrl.play_music()
        await websocket.send(json.dumps({"response": "音乐已开始播放"}))

    elif message["function"] == "pause_music":
        await audio_ctrl.pause_music()
        await websocket.send(json.dumps({"response": "音乐已暂停"}))

    elif message["function"] == "adjust_playback_time":
        await audio_ctrl.adjust_playback_time(message["time"])
        await websocket.send(json.dumps({"response": "播放时间已调整"}))

    elif message["function"] == "adjust_volume":
        await audio_ctrl.adjust_volume(
            message["volume_delta"], message["is_mic"])
        await websocket.send(json.dumps({"response": "音量已调整"}))

    elif message["function"] == "start_microphone_recording":
        await audio_ctrl.start_microphone_recording()
        await websocket.send(json.dumps({"response": "麦克风录音已开始"}))

    elif message["function"] == "stop_microphone_recording":
        await audio_ctrl.stop_microphone_recording()
        await websocket.send(json.dumps({"response": "麦克风录音已停止"}))

    elif message["function"] == "query_music_status":
        status = {
            "is_loading_audio": audio_ctrl.is_loading_audio,
            "is_music_playing": audio_ctrl.is_music_playing,
            "current_chunk_index": audio_ctrl.current_chunk_index,
            "total_chunks": audio_ctrl.total_chunks,
            "microphone_volume": audio_ctrl.microphone_volume,
            "music_volume": audio_ctrl.music_volume,
        }
        await websocket.send(json.dumps(status))

    await websocket.send(json.dumps({"response": "消息处理完成"}))


if __name__ == "__main__":
    # 监听所有公网 IP
    app.run(host="0.0.0.0",
            port=9000)
