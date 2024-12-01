from maindata.song import Song
from maindata.waitlist import WaitList
from maindata.active_song import ActiveSong
from maindata.mlibrary import MLibrary

from typing import *


class MainData:
    def __init__(self, db_path: str, music_path: str):
        self.mlibrary = MLibrary(db_path, music_path)
        self.waitlist = WaitList(db_path)
        self.active_song = ActiveSong()

    def waitlist_add(self, sid: int):
        song = self.mlibrary.fetch_songs_by_ids([sid])[0]
        if song == None:
            raise Exception(f"Song (sid {sid}) not found.")
        self.waitlist.add(song)
    
    def waitlist_move(self, wid: int, offset: int):
        self.waitlist.move(wid, offset)

    def waitlist_delete(self, wid: int):
        self.waitlist.delete(wid)

    def waitlist_get(self) -> list[Song]:
        return self.waitlist.get_song_list()
    
    def play(self, sid: int, time_stamp: int):
        song = self.mlibrary.fetch_songs_by_ids([sid])[0]
        if song == None:
            raise Exception(f"Song (sid {sid}) not found.")
        self.active_song.play(song, time_stamp)

    def pause(self, time: int):
        self.active_song.pause(time)

    def adjust_volume(self, volume: int):
        self.active_song.adjust_volume(volume)

    def fetch_songs_by_keyword(self, keyword: str) -> list[Song]:
        return self.mlibrary.fetch_songs_by_keyword(keyword)
    
    def fetch_songs_by_ids(self, sids: list[int])-> list[Optional[Song]]:
        return self.mlibrary.fetch_songs_by_ids(sids)

