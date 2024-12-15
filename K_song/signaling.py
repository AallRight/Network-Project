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
    audio_ctrl.create_play_thread()
    audio_ctrl.create_mic_thread()

    # temp function
    await audio_ctrl.play_audio()
    await audio_ctrl.load_local("music/时暮的思眷.wav")


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
            await audio_ctrl.add_track(connection_id, track)

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


@app.route("/play_local", methods=["POST"])
async def play_local():
    await audio_ctrl.play_local()
    return jsonify({"message": "Local audio playing"})


@app.route("/pause_local", methods=["POST"])
async def stop_local():
    await audio_ctrl.pause_local()
    return jsonify({"message": "Local audio stopped"})


@app.route("/adjust_time", methods=["POST"])
async def adjust_time():
    time = (await request.get_json()).get("time")
    await audio_ctrl.adjust_time(time)
    return jsonify({"message": "Time adjusted"})


@app.route("/mic_volume", methods=["POST"])
async def mic_volume():
    volume = (await request.get_json()).get("volume")
    await audio_ctrl.adjust_volume(volume, True)
    return jsonify({"message": "Mic volume adjusted"})


@app.route("/music_volume", methods=["POST"])
async def music_volume():
    volume = (await request.get_json()).get("volume")
    await audio_ctrl.adjust_volume(volume, False)
    return jsonify({"message": "Music volume adjusted"})


@app.route("/open_mic", methods=["POST"])
async def open_mic():
    await audio_ctrl.start_record()
    return jsonify({"message": "Mic opened"})


@app.route("/close_mic", methods=["POST"])
async def close_mic():
    await audio_ctrl.pause_record()
    return jsonify({"message": "Mic closed"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)
