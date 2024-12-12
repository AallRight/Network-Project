import pyaudio
import numpy as np
from av.audio.frame import AudioFrame
import asyncio
import wave
from audiomixer import AudioMixer
from audioplayer import AudioPlayer


class AudioCTRL:
    def __init__(self, sample_rate=48000, channels=2, buffer_size=10):
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

        # 运行标志
        self.running = True

        # 启动播放任务
        self.play_task = asyncio.create_task(self._play_audio())

    def load_local_audio(self, filepath):
        """
        加载本地音频文件（例如音乐）
        """
        with wave.open(filepath, "rb") as wf:
            if wf.getframerate() != self.sample_rate or wf.getnchannels() != self.channels:
                raise ValueError("本地音频文件的采样率或通道数与系统设置不一致")
            self.local_audio_data = wf.readframes(wf.getnframes())

    async def add_web_audio(self, frame: AudioFrame):
        """
        添加来自 WebRTC 的音频帧
        """
        audio_data = frame.to_ndarray()  # 转换为 NumPy 数组
        audio_data = np.tile(audio_data, (2, 1))  # 复制一份用于双声道播放
        if not self.buffer.full():
            await self.buffer.put(audio_data)
        else:
            print("警告: 缓冲区已满，丢弃音频帧")

    async def _play_audio(self):
        """
        播放协程：从缓冲区读取音频数据并输出
        """
        local_audio_index = 0
        local_audio_chunk = (
            np.frombuffer(self.local_audio_data,
                          dtype=np.int16) if self.local_audio_data else None
        )

        while self.running:

            if not self.buffer.empty():
                # 从缓冲区读取 WebRTC 音频
                web_audio = await self.buffer.get()

                # 从本地音频中提取对应大小的块
                if local_audio_chunk is not None:
                    chunk_size = web_audio.shape[1]
                    local_audio = local_audio_chunk[local_audio_index:local_audio_index + chunk_size]
                    local_audio = np.tile(local_audio, (2, 1))

                    if local_audio.shape[1] < chunk_size:
                        local_audio = np.pad(
                            local_audio, ((0, 0), (0, chunk_size - local_audio.shape[1])), mode="constant")

                    local_audio_index = (
                        local_audio_index + chunk_size) % len(local_audio_chunk)
                else:
                    local_audio = np.zeros_like(web_audio)

                # 混音
                mixed_audio = await self.mixer.mix_frames(
                    [
                        AudioFrame.from_ndarray(local_audio, 's16p'),
                        AudioFrame.from_ndarray(web_audio, 's16p')
                    ]
                )

                # 播放
                await self.player.play_frame(mixed_audio)
            else:
                await asyncio.sleep(0.01)  # 如果缓冲区为空，稍作等待

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

        # 加载本地音频文件
        audio_ctrl.load_local_audio("music/时暮的思眷.wav")

        # 模拟接收音频帧
        for _ in range(100000):
            silence = np.zeros((2, 480), dtype='int16')
            fake_frame = AudioFrame.from_ndarray(
                silence,
                's16p')
            await audio_ctrl.add_web_audio(fake_frame)
            await asyncio.sleep(0.01)  # 模拟 20ms 帧间隔

        await audio_ctrl.stop()

    asyncio.run(main())
