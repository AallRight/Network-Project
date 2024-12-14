import pyaudio
import numpy as np
from av.audio.frame import AudioFrame
import asyncio
import wave
from audiomixer import AudioMixer
from audioplayer import AudioPlayer
import aiofiles


class LocalAudio:
    def __init__(self,
                 sample_rate=48000,
                 channels=2,
                 chunk_size=1920):
        '''
        本地音频处理模块
        '''
        # 基础参数
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size

        self.local_audio_data = None
        self.chunk_num = 0

    async def load_local_audio(self, filepath):
        """
        异步加载本地音频文件（例如音乐）
        """
        # 使用 aiofiles 读取文件元数据
        async with aiofiles.open(filepath, "rb") as file:
            # 读取文件内容
            audio_data = await file.read()

        # 使用 wave 模块处理音频数据
        with wave.open(filepath, "rb") as wf:
            # 检查采样率
            if wf.getframerate() != self.sample_rate:
                raise ValueError("本地音频文件的采样率与系统设置不一致")

            # 获取文件帧数
            total_frames = wf.getnframes()

        # 异步处理音频数据
        self.local_audio_data = await self.process_audio_data(audio_data)

    async def process_audio_data(self, audio_data):
        """
        异步处理音频数据：转换为 np.ndarray 并分块
        """
        # 转换为 np.ndarray
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # 计算块数
        self.chunk_num = len(audio_array) // self.chunk_size + 1

        # 填充数据长度为块的整数倍
        audio_array = np.pad(
            audio_array,
            (0, self.chunk_num * self.chunk_size - len(audio_array)),
            'constant'
        )

        # 分块处理
        audio_array = audio_array.reshape(self.chunk_num, 1, -1)

        return audio_array


class AudioCTRL:
    def __init__(self,
                 sample_rate=48000,
                 channels=2,
                 buffer_size=1,
                 chunk_size=1920,
                 time_interval=0.001):
        """
        音频控制模块初始化
        """
        # 基础参数
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.time_interval = time_interval

        # 音频混合器
        self.mixer = AudioMixer(sample_rate=sample_rate, channels=channels)

        # 音频播放器
        self.player = AudioPlayer(sample_rate=sample_rate, channels=channels)

        # 音频缓冲区
        self.buffer_size = buffer_size
        self.web_buffer = asyncio.Queue(maxsize=buffer_size)
        self.local_buffer = asyncio.Queue(maxsize=buffer_size)

        # 加载本地音频文件
        self.local_audio = LocalAudio()

        # 运行标志
        self.running = True  # 是否播放声音标志
        self.playing = True  # 本地歌曲播放标志
        self.connecting = True  # 是否连接标志

    # * 总对外播放操作

    async def _play_audio(self):
        """
        播放协程：从缓冲区读取音频数据并输出
        """
        while self.running:

            web_chunk = None
            local_chunk = None
            mixed_chunk = None

            # 从web缓冲区读取音频
            if not self.web_buffer.empty():
                # 从缓冲区读取 WebRTC 音频
                web_chunk = await self.web_buffer.get()

            # 从本地缓冲区读取音频
            if not self.local_buffer.empty():
                local_chunk = await self.local_buffer.get()

            # 混音
            if web_chunk is not None and local_chunk is not None:
                mixed_chunk = await self.mixer.mix_frames(
                    [
                        local_chunk,
                        web_chunk
                    ]
                )
            elif web_chunk is not None:
                mixed_chunk = web_chunk
            elif local_chunk is not None:
                mixed_chunk = local_chunk

            # 播放
            if mixed_chunk is not None:
                await self.player.play_frame(mixed_chunk)
            else:
                await asyncio.sleep(self.time_interval / 4)

    async def play_audio(self):
        """
        启动播放任务
        """
        self.play_task = asyncio.create_task(self._play_audio())
        self.running = True

    async def stop_audio(self):
        """
        停止播放并释放资源
        """
        self.running = False
        self.playing = False
        self.connecting = False
        await self.play_task
        self.player.close()

    # * 本地歌曲操作

    async def load_local_audio(self, filepath):
        """
        异步加载本地音频文件（例如音乐）
        """
        await self.local_audio.load_local_audio(filepath)

    async def play_local(self):
        '''
        启动播放任务
        '''
        await self.load_local_audio("music/时暮的思眷.wav")
        asyncio.create_task(self.process_local())

        # 将本地歌曲播放标志设置为 True
        self.playing = True

    async def pause_local(self):
        '''
        暂停播放
        '''
        self.playing = False

    # * 音频连接和处理操作
    # * track1：webrtc音频
    # * track2：本地音频

    async def process_track(self, track):
        """
        处理音频轨道
        远程端的音频控制逻辑直接集成在process中
        1. 当远程pc连接时，就意味着connecting为True
        2. 当远程pc断开时，就意味着connecting为False
        """
        self.connecting = True
        # 实时接收音频并且处理
        while self.connecting and self.running:
            try:

                # 从音频轨道接收音频帧
                frame = await track.recv()
                audio_data = frame.to_ndarray()  # 转换为 NumPy 数组
                if self.web_buffer.full():
                    await self.web_buffer.get()

                # 将音频帧放入缓冲区
                await self.web_buffer.put(audio_data)
                await asyncio.sleep(self.time_interval)
            except Exception as e:
                # 出现错误时关闭
                print("The client break the connection or there is an error")
                self.connecting = False

    async def process_local(self):
        """
        处理本地音频
        """
        chunk_idx = 0
        # 实时将本地音频添加到缓冲区
        while self.playing and self.running:
            if self.local_audio.local_audio_data is not None:

                # 从本地音频中提取对应大小的块
                local_chunk = self.local_audio.local_audio_data[chunk_idx]
                chunk_idx += 1
                if self.local_buffer.full():
                    await self.local_buffer.get()

                # 将音频帧放入缓冲区
                await self.local_buffer.put(local_chunk)
            await asyncio.sleep(self.time_interval)


# 示例用法
if __name__ == "__main__":

    async def main():
        local = LocalAudio()
        await local.load_local_audio("music/时暮的思眷.wav")

    asyncio.run(main())
