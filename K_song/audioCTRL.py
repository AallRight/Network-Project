import pyaudio
import numpy as np
from av.audio.frame import AudioFrame
import asyncio
import wave
from audiomixer import AudioMixer
from audioplayer import AudioPlayer
from audiorecorder import AudioRecorder
import aiofiles
import logging
import threading

# 配置日志
logging.basicConfig(level=logging.INFO)


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

        # 音频录音器
        self.recorder = AudioRecorder(
            sample_rate=sample_rate, chunk_size=chunk_size, channels=channels)

        # 音频缓冲区
        self.buffer_size = buffer_size
        self.buffer = {}  # {connection_id: asyncio.Queue}
        self.local_microphone_id = "microphone"

        # 加载本地音频文件
        self.local_audio = LocalAudio()
        self.chunk_base = 0
        self.time_base = 0

        # 运行标志
        self.running = True  # 是否播放声音标志
        self.loading = False  # 是否加载音频文件标志
        self.playing = False  # 本地歌曲播放标志
        self.recording = False  # 麦克风录音标志

        # 新线程操作
        # 播放线程
        self.play_thread = None
        self.play_loop = None

        # 本地麦克风处理线程
        self.mic_thread = None
        self.mic_loop = None

    # * 新建新线程操作
    def start_loop(self, loop):
        '''
        启动新线程
        '''
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def create_play_thread(self):
        '''
        启动新线程
        '''
        loop = asyncio.new_event_loop()
        self.play_thread = threading.Thread(
            target=self.start_loop, args=(loop,))
        self.play_thread.start()
        self.play_loop = loop
        logging.info("The play thread is created")

        '''
        启动新线程
        '''
        loop = asyncio.new_event_loop()
        self.local_thread = threading.Thread(
            target=self.start_loop, args=(loop,))
        self.local_thread.start()
        self.local_loop = loop
        logging.info("The local thread is created")

    def create_mic_thread(self):
        '''
        启动新线程
        '''
        loop = asyncio.new_event_loop()
        self.mic_thread = threading.Thread(
            target=self.start_loop, args=(loop,))
        self.mic_thread.start()
        self.mic_loop = loop
        logging.info("The mic thread is created")

    # * 总对外播放操作

    async def _play_audio(self):
        """
        播放协程：从缓冲区读取音频数据并输出
        """
        while self.running:

            mixed_chunk = []
            last_chunk_idx = 0

            # 从缓冲区读取音频
            mixed_chunk = await asyncio.gather(
                *[self.buffer[id].get() for id in self.buffer if not self.buffer[id].empty()]
            )

            if self.running and self.playing and self.loading:
                chunk_idx = await self.get_chunk_idx()

                # overlap control
                if chunk_idx == last_chunk_idx:
                    await asyncio.sleep(self.time_interval)
                    continue
                last_chunk_idx = chunk_idx

                mixed_chunk.append(
                    self.local_audio.local_audio_data[chunk_idx])

            # 混音
            mixed_chunk = await self.mixer.mix_frames(mixed_chunk)

            # 播放
            if mixed_chunk is not None:
                await self.player.play_frame(mixed_chunk)
            else:
                await asyncio.sleep(self.time_interval/10)

    async def play_audio(self):
        """
        启动播放任务
        """
        # 开启新事件循环
        self.running = True
        asyncio.run_coroutine_threadsafe(self._play_audio(), self.play_loop)
        logging.info("The audio is playing")

    async def stop_audio(self):
        """
        停止播放并释放资源
        """
        self.running = False
        self.playing = False
        self.connecting = False
        self.player.close()
        logging.info("The audio is stopped")

    # * 本地歌曲操作

    async def load_local(self, filepath):
        """
        异步加载本地音频文件（例如音乐）
        """
        await self.local_audio.load_local_audio(filepath)
        self.loading = True

        # 将chunk_idx设置为0
        self.chunk_base = 0

        # 将time_base设置为当前时间
        self.time_base = asyncio.get_event_loop().time()

    async def play_local(self):
        '''
        启动播放任务
        '''
        # 判断本地音频是否加载
        if not self.loading:
            logging.info("The local audio is not loaded")
            return

        # 将time_base设置为当前时间
        self.time_base = asyncio.get_event_loop().time()
        logging.info(f"Time base is set to {self.time_base}")

        # 将本地歌曲播放标志设置为 True
        self.playing = True

    async def pause_local(self):
        '''
        暂停播放
        '''
        # 将本地歌曲播放标志设置为 False
        self.playing = False
        logging.info("The local audio is paused")

        # 设置chunk_base
        self.chunk_base = await self.get_chunk_idx()
        logging.info(f"Chunk base is set to {self.chunk_base}")

    async def adjust_time(self, time):
        '''
        调整播放时间
        '''
        # 计算调整的块数
        # ! 该时间是增量时间，而不是绝对时间
        chunk_num = int(time * self.sample_rate *
                        self.channels / self.chunk_size)
        # 调整chunk_base
        self.time_base = asyncio.get_event_loop().time()
        self.chunk_base += chunk_num
        self.chunk_base = max(
            0, min(self.chunk_base, self.local_audio.chunk_num - 1))
        logging.info(f"Time is adjusted to {self.time_base}")
        logging.info(f"Chunk base is set to {self.chunk_base}")

    # * 远程音频操作
    async def add_track(self, connection_id, track):
        """
        添加新的音轨，并启动其处理任务。
        """
        asyncio.create_task(self.process_track(connection_id, track))
        logging.info(f"Track {connection_id} is added and processing started.")

    # * 麦克风操作
    async def start_record(self):
        """
        启动麦克风录音
        """
        # 创建麦克风缓冲区
        self.buffer[self.local_microphone_id] = asyncio.Queue(
            maxsize=self.buffer_size)
        asyncio.run_coroutine_threadsafe(
            self.process_microphone(), self.mic_loop)
        logging.info("The microphone recording is started")

        # 将麦克风录音标志设置为 True
        self.recording = True

    async def pause_record(self):
        """
        停止麦克风录音
        """
        # 将麦克风录音标志设置为 False
        self.recording = False

        # 移除麦克风缓冲区
        self.buffer.pop(self.local_microphone_id)
        logging.info("The microphone recording is stopped")

    # * 音频连接和处理操作
    # * track1：webrtc音频
    # * track2：本地音乐音频
    # * track3：麦克风音频

    async def process_track(self, connection_id, track):
        """
        处理音频轨道
        远程端的音频控制逻辑直接集成在process中
        1. 当远程pc连接时，就意味着connecting为True
        2. 当远程pc断开时，就意味着connecting为False
        """

        # 创建该轨道的音频缓冲区
        self.buffer[connection_id] = asyncio.Queue(
            maxsize=self.buffer_size)
        logging.info(f"Buffer of {connection_id} is created")

        # 实时接收音频并且处理
        while self.running:
            try:
                # 从音频轨道接收音频帧
                frame = await track.recv()
                audio_data = frame.to_ndarray()  # 转换为 NumPy 数组
                if self.buffer[connection_id].full():
                    await self.buffer[connection_id].get()

                # 将音频帧放入缓冲区
                await self.buffer[connection_id].put(audio_data)
                await asyncio.sleep(self.time_interval)
            except Exception as e:
                # 出现错误时关闭
                self.buffer.pop(connection_id)
                logging.info(f"The buffer of {connection_id} is removed")
                break

        logging.info(f"Track {connection_id} processing is stopped")

    async def process_microphone(self):
        """
        处理麦克风音频
        """
        while self.recording and self.running:
            # 从麦克风录音
            audio_data = await self.recorder.record_frame()

            # 将音频帧放入缓冲区
            if self.buffer[self.local_microphone_id].full():
                await self.buffer[self.local_microphone_id].get()

            # 将音频帧放入缓冲区
            await self.buffer[self.local_microphone_id].put(audio_data)
            await asyncio.sleep(self.time_interval)
        logging.info("The microphone processing is stopped")

    # * 用于记时

    async def get_chunk_idx(self):
        """
        根据时间获取当前的块索引
        """
        chunk_idx = int((asyncio.get_event_loop().time() - self.time_base) *
                        self.sample_rate * self.channels / self.chunk_size) + self.chunk_base
        chunk_idx = max(0, min(chunk_idx, self.local_audio.chunk_num - 1))

        return chunk_idx


# 示例用法
if __name__ == "__main__":

    async def main():
        local = LocalAudio()
        await local.load_local_audio("music/时暮的思眷.wav")

    asyncio.run(main())
