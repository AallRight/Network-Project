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
    def __init__(self, sample_rate=48000, channels=2, chunk_size=1920):
        """
        本地音频处理模块
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_data = None
        self.total_chunks = 0

    async def load_audio_file(self, file_path):
        """
        异步加载本地音频文件
        """
        async with aiofiles.open(file_path, "rb") as file:
            audio_content = await file.read()

        with wave.open(file_path, "rb") as wave_file:
            if wave_file.getframerate() != self.sample_rate:
                raise ValueError("音频文件的采样率与系统设置不一致")

            total_frames = wave_file.getnframes()

        self.audio_data = await self._process_audio_data(audio_content)

    async def _process_audio_data(self, audio_content):
        """
        异步处理音频数据
        """
        audio_array = np.frombuffer(audio_content, dtype=np.int16)
        self.total_chunks = len(audio_array) // self.chunk_size + 1

        audio_array = np.pad(
            audio_array,
            (0, self.total_chunks * self.chunk_size - len(audio_array)),
            'constant'
        )

        return audio_array.reshape(self.total_chunks, 1, -1)


class AudioController:
    def __init__(self, sample_rate=48000, channels=2, buffer_capacity=1, chunk_size=1920, process_interval=0.001):
        """
        音频控制器模块
        """
        # 初始化音频控制器
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.process_interval = process_interval

        # 初始化音频混合器
        self.mixer = AudioMixer(sample_rate=sample_rate, channels=channels)

        # 初始化音频播放器
        self.player = AudioPlayer(sample_rate=sample_rate, channels=channels)

        # 初始化音频录制器
        self.recorder = AudioRecorder(
            sample_rate=sample_rate, chunk_size=chunk_size, channels=channels)

        # 初始化音频缓冲区
        self.buffer_capacity = buffer_capacity
        self.audio_buffers = {}
        self.microphone_id = "microphone"

        # 初始化本地音频处理模块
        self.local_audio = LocalAudio()

        # 初始化音频控制器状态
        self.current_chunk_index = 0
        self.music_volume = 0.5
        self.microphone_volume = 0.5
        self.max_volume = 2.0

        # 运行标志
        self.is_running = True
        self.is_loading_audio = False
        self.is_music_playing = False
        self.is_microphone_recording = False

        # 初始化音频控制器相关线程
        self.play_thread = None
        self.play_event_loop = None

        self.microphone_thread = None
        self.microphone_event_loop = None

    # * 线程创建相关方法
    def _start_event_loop_in_thread(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def create_play_thread(self):
        loop = asyncio.new_event_loop()
        self.play_thread = threading.Thread(
            target=self._start_event_loop_in_thread, args=(loop,))
        self.play_thread.start()
        self.play_event_loop = loop
        logging.info("播放线程已创建")

    def create_microphone_thread(self):
        loop = asyncio.new_event_loop()
        self.microphone_thread = threading.Thread(
            target=self._start_event_loop_in_thread, args=(loop,))
        self.microphone_thread.start()
        self.microphone_event_loop = loop
        logging.info("麦克风线程已创建")

    # * 音频控制器相关方法
    async def _play_audio_stream(self):
        while self.is_running:
            mixed_chunks = []

            if self.audio_buffers:
                mixed_chunks = await asyncio.gather(
                    *[self.audio_buffers[buffer_id].get() for buffer_id in self.audio_buffers if not self.audio_buffers[buffer_id].empty()]
                )

            if self.is_running and self.is_music_playing and self.is_loading_audio:
                self.current_chunk_index += 1
                mixed_chunks.append(
                    self.local_audio.audio_data[self.current_chunk_index] *
                    self.music_volume / self.microphone_volume
                )

            mixed_audio = await self.mixer.mix_frames(mixed_chunks)

            if mixed_audio is not None:
                await self.player.play_frame((mixed_audio * self.microphone_volume).astype(np.int16))
            else:
                await asyncio.sleep(self.process_interval / 10)

    async def start_audio_playback(self):
        self.is_running = True
        asyncio.run_coroutine_threadsafe(
            self._play_audio_stream(), self.play_event_loop)
        logging.info("音频播放已启动")

    async def stop_audio_playback(self):
        self.is_running = False
        self.is_music_playing = False
        self.player.close()
        logging.info("音频播放已停止")

    # * 本地音乐播放相关方法
    async def load_music_file(self, file_path):
        await self.local_audio.load_audio_file(file_path)
        self.is_loading_audio = True
        self.current_chunk_index = 0

    async def play_music(self):
        if not self.is_loading_audio:
            logging.info("未加载任何音频文件")
            return
        self.is_music_playing = True

    async def pause_music(self):
        self.is_music_playing = False
        logging.info("音乐播放已暂停")

    async def adjust_playback_time(self, time_offset):
        chunk_offset = int(time_offset * self.sample_rate *
                           self.channels / self.chunk_size)
        self.current_chunk_index += chunk_offset
        self.current_chunk_index = max(
            0, min(self.current_chunk_index, self.local_audio.total_chunks - 1))
        logging.info(f"当前播放块索引已调整至 {self.current_chunk_index}")

    async def adjust_volume(self, volume_delta, is_microphone=False):
        if is_microphone:
            self.microphone_volume += volume_delta
            self.microphone_volume = max(
                0, min(self.microphone_volume, self.max_volume))
            logging.info(f"麦克风音量调整为 {self.microphone_volume}")
        else:
            self.music_volume += volume_delta
            self.music_volume = max(0, min(self.music_volume, self.max_volume))
            logging.info(f"音乐音量调整为 {self.music_volume}")

    # * 远程音频流处理相关方法
    async def add_audio_track(self, connection_id, track):

        asyncio.create_task(self._process_audio_track(connection_id, track))
        logging.info(f"音频轨道 {connection_id} 已添加")

    # * 麦克风录音相关方法
    async def start_microphone_recording(self):

        self.audio_buffers[self.microphone_id] = asyncio.Queue(
            maxsize=self.buffer_capacity)
        logging.info("已创建麦克风音频缓冲区")

        asyncio.run_coroutine_threadsafe(
            self._process_microphone_audio(), self.microphone_event_loop)
        logging.info("麦克风录音已启动")

        self.is_microphone_recording = True

    async def stop_microphone_recording(self):
        self.is_microphone_recording = False
        self.audio_buffers.pop(self.microphone_id, None)
        logging.info("麦克风录音已停止")

    # * 音频流处理相关方法
    async def _process_audio_track(self, connection_id, track):
        self.audio_buffers[connection_id] = asyncio.Queue(
            maxsize=self.buffer_capacity)
        logging.info(f"已创远程音频流建缓冲区: {connection_id}")

        while self.is_running:
            try:
                frame = await track.recv()
                audio_data = frame.to_ndarray()
                if self.audio_buffers[connection_id].full():
                    await self.audio_buffers[connection_id].get()
                await self.audio_buffers[connection_id].put(audio_data)
                await asyncio.sleep(self.process_interval)
            except Exception as e:
                self.audio_buffers.pop(connection_id, None)
                logging.info(f"缓冲区 {connection_id} 已移除")
                break

        logging.info(f"音轨 {connection_id} 处理已停止")

    # * 麦克风音频处理相关方法
    async def _process_microphone_audio(self):
        while self.is_microphone_recording and self.is_running:
            try:
                audio_frame = await self.recorder.record_frame()

                if self.audio_buffers[self.microphone_id].full():
                    await self.audio_buffers[self.microphone_id].get()

                await self.audio_buffers[self.microphone_id].put(audio_frame)
                await asyncio.sleep(self.process_interval)
            except Exception as e:
                break

        logging.info("麦克风音频处理已停止")


if __name__ == "__main__":
    async def main():
        audio_controller = AudioController()
        await audio_controller.load_music_file("music/sample.wav")

    asyncio.run(main())
