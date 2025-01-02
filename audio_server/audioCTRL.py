import numpy as np
import asyncio
import noisereduce as nr
import logging
import threading
import librosa
import time
import traceback

from audio_server.audiomixer import AudioMixer
from audio_server.audioplayer import AudioPlayer
from audio_server.audiorecorder import AudioRecorder

from proto.binder import HandlerBinder
from proto.backend_message import AudioServerCommand

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

    def __chunk(self, audio: np.ndarray, chunk_size=960):
        num_chunks = (len(audio) + chunk_size - 1) // chunk_size
        padded_audio = np.zeros(num_chunks * chunk_size, dtype=np.float32)
        padded_audio[:len(audio)] = audio
        chunked_audio = padded_audio.reshape((num_chunks, 1, chunk_size))

        decay_length = len(audio) - (num_chunks - 1) * chunk_size
        decay = np.linspace(1, 0, decay_length, dtype=np.float32)
        chunked_audio[-1, 0, :decay_length] *= decay
        return chunked_audio, num_chunks

    def load_audio_file(self, file_path):
        if self.channels == 1:
            audio, sr = librosa.load(file_path, mono=True, sr=self.sample_rate, dtype=np.float32)
            self.audio_data, self.total_chunks = self.__chunk(audio, self.chunk_size)
        elif self.channels == 2:
            audio, sr = librosa.load(file_path, mono=False, sr=self.sample_rate, dtype=np.float32)
            if audio.shape[0] == 2:
                audio_data_0, num_chunks = self.__chunk(audio[0], self.chunk_size // 2)
                audio_data_1, num_chunks = self.__chunk(audio[1], self.chunk_size // 2)
                audio_data = np.empty((num_chunks, 1, self.chunk_size))
                audio_data[..., 0::2] = audio_data_0
                audio_data[..., 1::2] = audio_data_1
                self.audio_data, self.total_chunks = audio_data, num_chunks


class AudioController:
    def __init__(self, sample_rate=48000, channels=2, buffer_capacity=5, chunk_size=1920, process_interval=0.001):
        """
        音频控制器模块
        """
        self.handler = HandlerBinder(message_type=AudioServerCommand, oneof_field="command", obj=self)

        # 初始化音频控制器
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.process_interval = process_interval

        # 初始化音频混合器
        self.mixer = AudioMixer(sample_rate=sample_rate,
                                channels=channels, chunk_size=chunk_size)

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
        self.total_chunks = 0
        self.music_volume = 0.5
        self.microphone_volume = 0.5
        self.max_volume = 2.0

        # 运行标志
        self.is_running = True
        self.is_loading_audio = False
        self.is_music_playing = False
        self.is_microphone_recording = False
        self.if_denoise = False
        self.if_reverb = False

        # 初始化音频控制器相关线程
        self.play_thread = None
        self.play_event_loop = None

        self.microphone_thread = None
        self.microphone_event_loop = None

        self.print_time = True # 调试用

    async def execute(self, audio_server_command: AudioServerCommand):
        try:
            return await self.handler.async_handle(audio_server_command)
        except Exception as e:
            raise Exception(f"Failed to execute audio server command. (command: >>> {audio_server_command} <<<)") from e

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
        try:
            while self.is_running:
                mixed_chunks = []

                # human voice
                if self.audio_buffers:
                    mixed_chunks = await asyncio.gather(
                        *[self.audio_buffers[buffer_id].get() for buffer_id in self.audio_buffers if not self.audio_buffers[buffer_id].empty()]
                    )
                
                indices = [chunk[1] for chunk in mixed_chunks]
                mixed_chunks = [chunk[0] for chunk in mixed_chunks]
                
                # local music
                if self.is_running and self.is_music_playing and self.is_loading_audio and self.current_chunk_index < self.total_chunks:
                    self.current_chunk_index += 1
                    mixed_chunks.append(
                        self.local_audio.audio_data[self.current_chunk_index] *
                        self.music_volume / self.microphone_volume
                    )
                else:
                    mixed_chunks.append(
                        np.zeros((1, self.chunk_size), dtype=np.float32))
                    
                # mix audio
                mixed_audio = self.mixer.mix_frames(mixed_chunks,
                                                    if_reverb=self.if_reverb)
            

                if mixed_audio is not None:
                    self.player.play_frame(
                        (mixed_audio * self.microphone_volume))
                    if len(indices) > 0 and self.print_time:
                        print("consumer play", indices, time.time())
                    await asyncio.sleep(self.process_interval / 10)
                else:
                    await asyncio.sleep(self.process_interval / 10)
        except Exception as e:
            traceback.print_exc()

    async def start_audio_playback(self):
        self.is_running = True
        asyncio.create_task(
            self._play_audio_stream())
        logging.info("音频播放已启动")

    async def stop_audio_playback(self):
        self.is_running = False
        self.is_music_playing = False
        self.player.close()
        logging.info("音频播放已停止")

    # * 本地音乐播放相关方法
    async def load_music_file(self, file_path):
        self.local_audio.load_audio_file(file_path)
        self.total_chunks = self.local_audio.total_chunks
        self.is_loading_audio = True
        self.current_chunk_index = 0

    async def play_music(self, at_time):
        if not self.is_loading_audio:
            logging.info("未加载任何音频文件")
            return
        self.current_chunk_index = int(
            (at_time/1000) * self.sample_rate * self.channels / self.chunk_size)
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

        asyncio.create_task(
            self._process_microphone_audio())
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

        idx = 0
        while self.is_running:
            try:
                frame = await track.recv()
                audio_data = frame.to_ndarray()
                if self.audio_buffers[connection_id].full():
                    await self.audio_buffers[connection_id].get()
                    print("producer drop", idx, time.time())
                await self.audio_buffers[connection_id].put((audio_data, idx))
                print("producer put", idx, time.time())
                await asyncio.sleep(self.process_interval / 10)
                idx += 1
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

                # 降噪处理
                if self.if_denoise:
                    audio_frame = nr.reduce_noise(
                        audio_frame, sr=self.sample_rate)

                if self.audio_buffers[self.microphone_id].full():
                    await self.audio_buffers[self.microphone_id].get()

                await self.audio_buffers[self.microphone_id].put(audio_frame)
                await asyncio.sleep(self.process_interval)
            except Exception as e:
                break

        logging.info("麦克风音频处理已停止")

    # * 其他设置内容

    async def if_denoise(self, if_denoise):
        self.if_denoise = if_denoise
        logging.info(f"降噪处理已设置为 {if_denoise}")

    async def if_reverb(self, if_reverb):
        self.if_reverb = if_reverb
        logging.info(f"混响处理已设置为 {if_reverb}")
