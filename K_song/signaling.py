import asyncio
import logging
from quart import Quart, request, jsonify
from quart_cors import cors
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaPlayer, MediaRecorder
import pyaudio

app = Quart(__name__)
app = cors(app, allow_origin="*")
ice_candidates = []

# 配置日志
logging.basicConfig(level=logging.INFO)

pc = RTCPeerConnection()


@app.route("/ice-candidate", methods=["POST"])
async def ice_candidate():
    # ICE candidate 交换
    data = await request.get_json()
    candidate = data.get("candidate")
    ice_candidates.append(candidate)
    return "Candidate received", 200


@app.route("/offer", methods=["POST"])
async def offer():
    # 接收到offer后返回answer

    offer_sdp = (await request.get_json()).get("sdp")

    # 创建新的 RTCPeerConnection 实例
    pc = RTCPeerConnection()

    @pc.on("track")
    async def on_track(track):
        # # 接收到音频轨道后开始录制
        if track.kind == "audio":

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,  # 假设音频是 16 位 PCM 格式
                            channels=1,  # 假设是单声道音频
                            rate=48000,  # 假设采样率是 48000 Hz
                            output=True)

            # 实时接收和播放音频帧
            while True:
                frame = await track.recv()
                # 将音频帧写入到音频流
                stream.write(frame.to_ndarray().tobytes())
        # if track.kind == "audio":
        #     recorder = MediaRecorder("output.wav")
        #     recorder.addTrack(track)
        #     await recorder.start()
        #     await asyncio.sleep(5)
        #     await recorder.stop()
        #     logging.info("Audio recorded")
        # if track.kind == "audio":
        #     logging.info("Audio track received, starting recording")
        #     player = MediaPlayer("test.wav")
        #     temp_track = player.audio

        #     recorder = MediaRecorder("received_audio.wav")
        #     recorder.addTrack(temp_track)
        #     await recorder.start()
        #     await asyncio.sleep(1)  # 模拟录制时长
        #     await recorder.stop()
        #     logging.info("Recording stopped and saved")

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type="offer"))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)
