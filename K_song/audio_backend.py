from typing import *
import time
import threading
import websockets
import logging
import json

# from server.constant import *

# * 使用 websocket 和 AudioCTRL 进程间通信
url_ctrl = "wss://0.0.0.0:9002/audio_ctrl"


async def send_to_CTRL(message):
    # 连接到音频控制器
    socket_ctrl = await websockets.connect(url_ctrl, origin="https://0.0.0.0:9003")
    logging.info("连接到音频控制器")

    await socket_ctrl.send(json.dumps(message))
    logging.info(f"发送到音频控制器: {message}")

    response_string = await socket_ctrl.recv()
    response = json.loads(response_string)
    logging.info(f"收到音频控制器响应: {response}")

    await socket_ctrl.close()
    logging.info("与音频控制器断开连接")

    return response

# ad-hoc audio backend


class AudioBackend:
    def __init__(self, play_next_callback: Callable[[], None]):
        self.song_path: Optional[str] = None
        self.track_length: Optional[float] = None
        self.is_pause: bool = True
        self.time: Optional[int] = 0
        self.time_stamp: Optional[int] = None
        self.play_next_callback: Callable[[], None] = play_next_callback
        self.mic_volume: int = 50
        self.music_volume: int = 50

        self.stop_event = threading.Event()
        self.audio_backend_loop = None

    def play(self, song_path: str, at_time: int, track_length: float) -> int:
        if self.song_path:
            # 加载音乐文件前先暂停当前音乐
            send_to_CTRL({"function": "pause_music"})

        if True:  # TODO: 加个判断用于是否重新加载音乐文件
            send_to_CTRL(
                {"function": "load_music_file", "file_path": song_path})
        send_to_CTRL({"function": "play_music"})
        self.song_path = song_path
        self.track_length = track_length
        self.is_pause = False
        self.time = None
        self.time_stamp = int(time.time() * 1000) - at_time
        self.__start_audio_backend_loop()
        return self.time_stamp

    def pause(self) -> int:
        if not self.is_pause:
            if self.song_path:
                send_to_CTRL({"function": "pause_music"})
            self.is_pause = True
            self.time = int(time.time() * 1000) - self.time_stamp
            self.time_stamp = None
            self.__stop_audio_backend_loop()
        return self.time

    def jump(self, to_time: int) -> Tuple[bool, int]:
        if self.is_pause:
            if self.song_path:
                time_offset = to_time - self.time
                send_to_CTRL(
                    {"function": "adjust_playback_time", "time": time_offset})
                self.time = to_time
            return self.is_pause, self.time
        else:
            self.time_stamp = self.play(
                self.song_path, to_time, self.track_length)
            return self.is_pause, self.time_stamp

    def set_mic_volume(self, volume: int):
        volume = max(0, min(100, volume))
        send_to_CTRL({"function": "adjust_volume",
                      "volume_delta": (volume - self.mic_volume)/100, "is_mic": True})
        self.mic_volume = volume

    def set_music_volume(self, volume: int):
        self.music_volume = max(0, min(100, volume))
        send_to_CTRL({"function": "adjust_volume",
                      "volume_delta": (volume - self.music_volume)/100, "is_mic": False})

     # ? 开启麦克风录音
    def open_mic(self):
        send_to_CTRL({"function": "start_microphone_recording"})

    # ? 关闭麦克风录音
    def close_mic(self):
        send_to_CTRL({"function": "stop_microphone_recording"})

    def __start_audio_backend_loop(self):
        self.stop_event.clear()
        self.audio_backend_loop = threading.Thread(
            target=self.__audio_backend_loop, daemon=True)
        self.audio_backend_loop.start()

    def __stop_audio_backend_loop(self):
        self.stop_event.set()

    def __audio_backend_loop(self):
        while not self.stop_event.is_set():
            if not self.is_pause and time.time() * 1000 - self.time_stamp > self.track_length * 1000:
                self.play_next_callback()
            time.sleep(1)
