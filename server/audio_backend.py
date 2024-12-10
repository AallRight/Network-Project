from typing import *
import time
import pygame
import threading

from server.constant import *

# ad-hoc audio backend
class AudioBackend:
    def __init__(self, play_next_callback: Callable[[], None]):
        self.song_path: Optional[str] = None
        self.track_length: Optional[float] = None
        self.is_pause: bool = True
        self.time: Optional[int] = 0
        self.time_stamp: Optional[int] = None
        self.play_next_callback: Callable[[], None] = play_next_callback

        pygame.init()
        pygame.mixer.init()

        self.stop_event = threading.Event()
        self.audio_backend_loop = None

    def play(self, song_path: str, at_time: int, track_length: float) -> int:
        if self.song_path:
            pygame.mixer.music.stop()
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(start=at_time / 1000.0)
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
                pygame.mixer.music.stop()
            self.is_pause = True
            self.time = int(time.time() * 1000) - self.time_stamp
            self.time_stamp = None
            self.__stop_audio_backend_loop()
        return self.time
    
    def jump(self, to_time: int) -> Tuple[bool, int]:
        if self.is_pause:
            if self.song_path:
                self.time = to_time
            return self.is_pause, self.time
        else:
            self.time_stamp = self.play(self.song_path, to_time, self.track_length)
            return self.is_pause, self.time_stamp
        
    def set_volume(self, volume: int):
        self.volume = max(0, min(100, volume))
        pygame.mixer.music.set_volume(self.volume / 100.0)

    def __start_audio_backend_loop(self):
        self.stop_event.clear()
        self.audio_backend_loop = threading.Thread(target=self.__audio_backend_loop, daemon=True)
        self.audio_backend_loop.start()
    
    def __stop_audio_backend_loop(self):
        self.stop_event.set()

    def __audio_backend_loop(self):
        while not self.stop_event.is_set():
            if not self.is_pause and time.time() * 1000 - self.time_stamp > self.track_length * 1000:
                self.play_next_callback()
            time.sleep(1)