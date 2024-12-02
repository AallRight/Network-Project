from typing import *
import time

class AudioServer:
    def __init__(self, on_finish: Callable):
        self.song_path: Optional[str] = None
        self.is_pause: bool = True
        self.time: Optional[int] = 0
        self.time_stamp: Optional[int] = None
        self.on_finish: Callable = on_finish

    def play(self, song_path: str) -> int:
        self.song_path = song_path
        self.is_pause = False
        self.time = None
        self.time_stamp = int(time.time() * 1000)
        return self.time_stamp
    
    def pause(self) -> int:
        self.is_pause = True
        self.time = int(time.time() * 1000) - self.time_stamp
        self.time_stamp = None
        return self.time
    
    def jump(self, time: int) -> Tuple[bool, int]:
        if self.is_pause:
            self.time = time
            return self.is_pause, self.time
        else:
            self.time_stamp = int(time.time() * 1000) - time
            return self.is_pause, self.time_stamp
        
    def adjust_volume(self, volume: int):
        self.volume = max(0, min(100, volume))