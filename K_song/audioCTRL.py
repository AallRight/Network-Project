import pyaudio
import numpy as np
from av.audio.frame import AudioFrame
import asyncio
import wave
from audiomixer import AudioMixer
from audioplayer import AudioPlayer


class AudioCTRL:
    def __init__(self,
                 sample_rate=48000,
                 channels=2,
                 buffer_size=10):
        """
        音频控制模块初始化
        """
        # 基础参数
        self.sample_rate = sample_rate
        self.channels = channels

        # 音频混合器
        self.mixer = AudioMixer(sample_rate=sample_rate, channels=channels)

        # 音频播放器
        self.player = AudioPlayer(sample_rate=sample_rate, channels=channels)

        # 音频缓冲区
        self.buffer_size = buffer_size
        self.buffer = asyncio.Queue(maxsize=buffer_size)

        # 本地音乐数据
        self.local_audio_data = None
        self.local_audio_length = 0

        # 加载本地音频文件
        self.load_local_audio("music/时暮的思眷.wav")

        # 启动播放任务
        self.play_task = asyncio.create_task(self._play_audio())

        # 运行标志
        self.running = True

    def load_local_audio(self, filepath):
        """
        加载本地音频文件（例如音乐）
        """
        with wave.open(filepath, "rb") as wf:
            if wf.getframerate() != self.sample_rate:
                raise ValueError("本地音频文件的采样率与系统设置不一致")
            self.local_audio_data = wf.readframes(wf.getnframes())

            # 将local audio 预先处理成 np.ndarray， 以便后续使用
            self.local_audio_data = np.frombuffer(
                self.local_audio_data, dtype=np.int16)
            self.local_audio_length = len(self.local_audio_data)

            # 将local audio 后面补零，以便后续使用
            self.local_audio_data = np.pad(
                self.local_audio_data, (0, 1024), 'constant')

            self.local_audio_data = self.local_audio_data.reshape(1, -1)

    async def add_web_audio(self, frame: AudioFrame):
        """
        添加来自 WebRTC 的音频帧
        """
        audio_data = frame.to_ndarray()  # 转换为 NumPy 数组
        if self.buffer.full():
            await self.buffer.get()  # 如果缓冲区满，弹出最早的音频帧

        # 将音频帧放入缓冲区
        await self.buffer.put(audio_data)

    async def _play_audio(self):
        """
        播放协程：从缓冲区读取音频数据并输出
        """
        local_audio_index = 0

        while self.running:

            if not self.buffer.empty():
                # 从缓冲区读取 WebRTC 音频
                web_audio = await self.buffer.get()

                # 从本地音频中提取对应大小的块
                local_audio = None
                if self.local_audio_data is not None:
                    chunk_size = web_audio.shape[1]
                    local_audio = self.local_audio_data[:,
                                                        local_audio_index:local_audio_index + chunk_size]

                    local_audio_index = (
                        local_audio_index + chunk_size) % self.local_audio_length
                else:
                    local_audio = np.zeros_like(web_audio)

                # 混音
                mixed_audio = await self.mixer.mix_frames(
                    [
                        local_audio,
                        web_audio
                    ]
                )

                # 播放
                await self.player.play_frame(mixed_audio)
            await asyncio.sleep(0.001)  # 如果缓冲区为空，稍作等待

    async def process_track(self, track):
        """
        处理音频轨道
        """
        # 实时接收音频并且处理
        while self.running:
            try:
                frame = await track.recv()
                await self.add_web_audio(frame)
            except Exception as e:
                print("The client break the connection or there is an error")
                self.running = False

    async def stop(self):
        """
        停止播放并释放资源
        """
        self.running = False
        await self.play_task
        self.player.close()


# 示例用法
if __name__ == "__main__":
    async def main():
        audio_ctrl = AudioCTRL()

        # 模拟接收音频帧
        for _ in range(10000):
            silence = np.zeros((1, 1920), dtype=np.int16)
            fake_frame = AudioFrame.from_ndarray(
                silence,
                's16',
                layout='mono')
            await audio_ctrl.add_web_audio(fake_frame)
            await asyncio.sleep(0.01)  # 模拟 20ms 帧间隔

        await audio_ctrl.stop()

    asyncio.run(main())
