import logging
from quart import Quart, request, jsonify, websocket, send_from_directory
from quart_cors import cors
from aiortc import RTCPeerConnection, RTCSessionDescription
import json
import uuid
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.dont_write_bytecode = True

from audio_server.audioCTRL import AudioController
from proto.backend_message import AudioServerCommand

# 创建 Quart 应用
app = Quart(__name__)
app = cors(app, allow_origin="*", allow_methods="*", allow_headers="*")

# 配置日志
logging.basicConfig(level=logging.INFO)

# 存储多个连接
pcs = {}  # {connection_id: RTCPeerConnection}


# 创建音频控制器实例
audio_ctrl = AudioController(buffer_capacity=10,
                             sample_rate=48000,
                             process_interval=0.001,
                             chunk_size=1920)

# 配置日志
logging.basicConfig(level=logging.INFO)


@app.before_serving
async def initial_device():
    """初始化音频控制器"""
    audio_ctrl.create_play_thread()
    audio_ctrl.create_microphone_thread()

    await audio_ctrl.start_audio_playback()


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


# 音频控制
@app.route('/audio_ctrl', methods=['POST'])
async def audio_control():
    command_bytes = await request.get_data()
    if not command_bytes:
        return jsonify({"status": "failed", "message": "No command provided"}), 400
    audio_server_command = AudioServerCommand()
    try:
        audio_server_command.ParseFromString(command_bytes)
        print(audio_server_command)
        await audio_ctrl.execute(audio_server_command)
        logging.info(f"成功执行客户端命令: {audio_server_command}")
        return jsonify({"status": "success"})
    except Exception as e:
        logging.error(f"执行客户端命令失败, 错误: {e}")
        return jsonify({"status": "failed", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=9000)
