import asyncio
import logging
from quart import Quart, request, jsonify
from quart_cors import cors
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaPlayer, MediaRecorder
from audio import AudioProcessor
import time
import json

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

    # ? 延时测试
    # @pc.on("datachannel")
    # def on_datachannel(channel):
    #     @channel.on("message")
    #     def on_message(message):
    #         received_timestamp = int(time.time() * 1000)  # 接收端时间戳
    #         message_data = json.loads(message)  # 解析 JSON 字符串
    #         sent_timestamp = message_data["timestamp"]  # 提取发送端时间戳
    #         latency = received_timestamp - sent_timestamp
    #         print(f"Latency: {latency:.2f} ms")

    @pc.on("track")
    async def on_track(track):
        # # 接收到音频轨道后开始录制
        if track.kind == "audio":

            try:
                # 先获取一个音频帧，用于获取音频参数
                standard_frame = await track.recv()
                logging.info(f"timebase: {standard_frame.time_base}, "
                             f"format: {standard_frame.format}, "
                             f"pts: {standard_frame.pts}, "
                             f"sample_rate: {standard_frame.sample_rate}")

                # 创建音频处理器
                processor = AudioProcessor(
                    buffer_size=1,
                    sample_rate=standard_frame.sample_rate,
                    channels=2
                )

                # 实时接收音频并且处理
                await processor.process_track(track)

            # 关闭音频处理器
            except Exception as e:
                logging.info(f"Track processing ended: {e}")
            finally:
                processor.close()

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type="offer"))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)
