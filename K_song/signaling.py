import asyncio
import logging
from quart import Quart, request, jsonify
from quart_cors import cors
from aiortc import RTCPeerConnection, RTCSessionDescription
from audioCTRL import AudioCTRL
import json
import uuid

app = Quart(__name__)
app = cors(app, allow_origin="*")

# 配置日志
logging.basicConfig(level=logging.INFO)

# 存储多个连接
pcs = {}  # {connection_id: RTCPeerConnection}

# 创建 AudioCTRL 实例
audio_ctrl = AudioCTRL(buffer_size=1, sample_rate=48000)


@app.before_serving
async def start_audio_ctrl():
    # temp function
    await audio_ctrl.play_audio()
    await audio_ctrl.play_local()


@app.route("/offer", methods=["POST"])
async def offer():
    # 接收到 offer 后返回 answer
    offer_sdp = (await request.get_json()).get("sdp")

    # 创建新的 RTCPeerConnection 实例
    connection_id = str(uuid.uuid4())
    pc = RTCPeerConnection()
    pcs[connection_id] = pc  # 保存连接到字典中
    logging.info(f"Connection {connection_id} created")

    @pc.on("track")
    async def on_track(track):
        if track.kind == "audio":
            await audio_ctrl.process_track(connection_id, track)

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type="offer"))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
        "connection_id": connection_id  # 返回连接 ID
    })


@app.route("/ice-candidate/<connection_id>", methods=["POST"])
async def ice_candidate(connection_id):
    # ICE candidate 交换
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
    # 关闭指定连接
    if connection_id in pcs:
        pc = pcs.pop(connection_id)  # 从字典中删除连接
        await pc.close()
        logging.info(f"Connection {connection_id} closed")
        return jsonify({"message": "Connection closed"})
    else:
        return jsonify({"message": "Connection not found"}), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)
