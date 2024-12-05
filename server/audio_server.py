from typing import *
import time
import pygame
import threading

# ad-hoc audio server
class AudioServer:
    def __init__(self):
        self.song_path: Optional[str] = None
        self.is_pause: bool = True
        self.time: Optional[int] = 0
        self.time_stamp: Optional[int] = None
        pygame.mixer.init()

        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

    def play(self, song_path: str, at_time: int) -> int:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(start=at_time / 1000)
        self.song_path = song_path
        self.is_pause = False
        self.time = None
        self.time_stamp = int(time.time() * 1000) - at_time
        return self.time_stamp
    
    def pause(self) -> int:
        if not self.is_pause:
            if self.song_path:
                pygame.mixer.music.pause()
            self.is_pause = True
            self.time = int(time.time() * 1000) - self.time_stamp
            self.time_stamp = None
        return self.time
    
    def jump(self, to_time: int) -> Tuple[bool, int]:
        if self.song_path:
            pygame.mixer.music.pause()
        if self.is_pause:
            self.time = to_time
            return self.is_pause, self.time
        else:
            self.time_stamp = int(time.time() * 1000) - to_time
            return self.is_pause, self.time_stamp
        
    def set_volume(self, volume: int):
        self.volume = max(0, min(100, volume))