from typing import *
import time
import threading
import requests

from server.constant import *
from proto.backend_message import *


class AudioBackend:
    def __init__(
        self,
        play_next_callback: Callable[[], None],
        audio_server_url: str = "http://0.0.0.0:5000/audio_ctrl",
    ):
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

        self.audio_server_url = audio_server_url

        self.recording = False

    def play(self, song_path: str, at_time: int, track_length: float) -> int:
        if self.song_path:
            self.__send_to_audio_server(AudioServerCommand(pause_music=PauseMusic()))
        if True:
            self.__send_to_audio_server(
                AudioServerCommand(load_music_file=LoadMusicFile(file_path=song_path))
            )
        self.__send_to_audio_server(
                AudioServerCommand(play_music=PlayMusic(at_time=at_time))
            )

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
                self.__send_to_audio_server(
                    AudioServerCommand(pause_music=PauseMusic())
                )
            self.is_pause = True
            self.time = int(time.time() * 1000) - self.time_stamp
            self.time_stamp = None
            self.__stop_audio_backend_loop()
        return self.time

    def jump(self, to_time: int) -> Tuple[bool, int]:
        if self.is_pause:
            if self.song_path:
                time_offset = to_time - self.time
                self.__send_to_audio_server(
                    AudioServerCommand(
                        adjust_playback_time=AdjustPlaybackTime(time_offset=time_offset)
                    )
                )
                self.time = to_time
            return self.is_pause, self.time
        else:
            self.time_stamp = self.play(self.song_path, to_time, self.track_length)
            return self.is_pause, self.time_stamp

    def set_mic_volume(self, volume: int):
        volume = max(0, min(100, volume))
        self.__send_to_audio_server(
            AudioServerCommand(
                adjust_volume=BackendAdjustVolume(
                    volume_delta=(volume - self.mic_volume) / 100.0, is_microphone=True
                )
            )
        )
        self.mic_volume = volume

    def set_volume(self, volume: int):
        self.__send_to_audio_server(
            AudioServerCommand(
                adjust_volume=BackendAdjustVolume(
                    volume_delta=(volume - self.music_volume) / 100.0, is_microphone=False
                )
            )
        )
        self.music_volume = max(0, min(100, volume))

    def switch_recording(self):
        if self.recording:
            self.__send_to_audio_server(
                AudioServerCommand(
                    stop_microphone_recording=StopMicrophoneRecording()
                )
            )
            self.recording = False
        else:
            self.__send_to_audio_server(
                AudioServerCommand(
                    start_microphone_recording=StartMicrophoneRecording()
                )
            )
            self.recording = True

    def __send_to_audio_server(self, command: AudioServerCommand):
        try:
            response = requests.post(self.audio_server_url, data=command.SerializeToString())
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            raise Exception(f"Audio server HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            raise Exception(f"Audio backend request error: {req_err}") from req_err


    def __start_audio_backend_loop(self):
        self.stop_event.clear()
        self.audio_backend_loop = threading.Thread(
            target=self.__audio_backend_loop, daemon=True
        )
        self.audio_backend_loop.start()

    def __stop_audio_backend_loop(self):
        self.stop_event.set()

    def __audio_backend_loop(self):
        while not self.stop_event.is_set():
            if (
                not self.is_pause
                and time.time() * 1000 - self.time_stamp > self.track_length * 1000
            ):
                self.play_next_callback()
            time.sleep(1)
