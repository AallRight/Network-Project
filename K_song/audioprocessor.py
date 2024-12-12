import pyaudio
from av.audio.frame import AudioFrame
import asyncio
from audioplayer import AudioPlayer
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

        self.player = AudioPlayer(format=format,
                                  sample_rate=sample_rate,
                                  channels=channels)

    def add_frame(self, frame: AudioFrame):
        # 添加音频帧到缓冲区
        if len(self.buffer) >= self.buffer_size:
            self.buffer.pop(0)  # 丢弃旧帧
        self.buffer.append(frame)

    async def play_audio(self):
        # 异步播放音频
        while True:
            if self.buffer:
                frame = self.buffer.pop(0)
                audio_data = frame.to_ndarray()
                await self.player.play_frame(audio_data)

            await asyncio.sleep(0.001)  # 避免 CPU 100% 占用

    async def process_track(self, track):
        # 处理音频轨道
        asyncio.create_task(self.play_audio())  # 异步播放音频
        while True:
            frame = await track.recv()
            self.add_frame(frame)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
