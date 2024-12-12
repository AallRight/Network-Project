import pyaudio
from av.audio.frame import AudioFrame
import asyncio
import time


class AudioProcessor:
    def __init__(self, format=pyaudio.paInt16,
                 buffer_size=1,
                 sample_rate=48000,
                 channels=2):
        # 初始化音频处理器
        self.buffer = []
        self.format = format
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.channels = channels

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=format,
                                  channels=channels,
                                  rate=sample_rate,
                                  output=True)

        # 用于debug
        self.if_time_stamp = False
        self.if_stream = True

    def add_frame(self, frame: AudioFrame):
        # 添加音频帧到缓冲区
        if len(self.buffer) >= self.buffer_size:
            self.buffer.pop(0)  # 丢弃旧帧
        self.buffer.append(frame)

    async def play_audio(self):
        # 异步播放音频
        while self.if_stream:
            if self.buffer:
                frame = self.buffer.pop(0)

                audio_data = frame.to_ndarray()
                self.stream.write(audio_data.tobytes())

                # 获取时间戳
                if self.if_time_stamp and frame.pts % 1000 == 0:
                    timestamp = time.time()
                    print(frame.pts, int(timestamp * 1000))

            await asyncio.sleep(0.001)  # 避免 CPU 100% 占用

    async def process_track(self, track):
        # 处理音频轨道
        asyncio.create_task(self.play_audio())  # 异步播放音频
        while self.if_stream:

            # 获取音频帧
            frame = await track.recv()

            # 获取时间戳
            if self.if_time_stamp and frame.pts % 1000 == 0:
                timestamp = time.time()
                print(frame.pts, int(timestamp * 1000))

            self.add_frame(frame)

    def close(self):
        self.if_stream = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        print("AudioProcessor closed")
