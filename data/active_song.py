from typing import *
import json
from data.song import Song
from dataclasses import asdict

class ActiveSong:
    def __init__(self):
        self.song: Optional[Song] = None
        self.is_pause: bool = True
        self.time: Optional[int] = 0
        self.time_stamp: Optional[int] = None
        self.volume = 50
        
    def play(self, song: Song, time_stamp: int):
        self.song = song
        self.is_pause = False
        self.time = None
        self.time_stamp = time_stamp

    def pause(self, time: int):
        self.is_pause = True
        self.time = time
        self.time_stamp = None

    def set_volume(self, volume: int):
        self.volume = max(0, min(100, volume))
    

    def serialize(self) -> dict:
        return json.dumps({
            'song': asdict(self.song) if self.song else None,
            'is_pause': self.is_pause,
            'time': self.time,
            'time_stamp': self.time_stamp,
            'volume': self.volume
        })

    @staticmethod
    def deserialize(json_str: str) -> 'ActiveSong':
        try:
            data = json.loads(json_str)
            active_song = ActiveSong()
            active_song.is_pause = data.get('is_pause', True)
            active_song.time = data.get('time', 0)
            active_song.time_stamp = data.get('time_stamp', None)
            active_song.volume = data.get('volume', 50)
            if data.get('song'):
                active_song.song = Song(**data['song'])
            return active_song
        except (json.JSONDecodeError, TypeError) as e:
            raise Exception(f"Failed to deserialize from JSON {json_str}") from e
        
    def __str__(self) -> str:
        return f"{self.song}" \
               f", pause or not {self.is_pause}"\
               f", pauses at {self.time}"\
               f", starts at {self.time_stamp}"\
               f", volume {self.volume}"
               
               
