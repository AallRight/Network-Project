from mlibrary import Mlibrary
from wait_list import WaitList
from active_song import ActiveSong


class MainData:
    """核心数据和操作"""
    def __init__(self):
        self.mlibrary = Mlibrary()
        self.wait_list = WaitList()
        self.active_song = ActiveSong()

    # Mlibrary API
    def add_to_library(self, sid, path, title, artist, album, track_length, sample_rate):
        self.mlibrary.add_song(sid, path, title, artist, album, track_length, sample_rate)

    # Wait_List API
    def wait_list_add(self, sid):
        if self.mlibrary.get_song(sid):
            self.wait_list.add(sid)
        else:
            raise ValueError("Song ID not found in Library")

    def wait_list_move(self, wid, offset):
        self.wait_list.move(wid, offset)

    def wait_list_delete(self, wid):
        self.wait_list.delete(wid)

    # Active_Song API
    def active_song_play(self):
        if not self.wait_list.get_list():
            raise ValueError("Wait list is empty")
        sid = self.wait_list.get_list()[0]
        self.active_song.play(sid)

    def active_song_pause(self):
        self.active_song.pause_song()

    def active_song_adjust_vol(self, volume):
        self.active_song.adjust_vol(volume)

    def active_song_adjust_time(self, time_position):
        self.active_song.adjust_time(time_position)

    # Additional Utility
    def get_active_song_status(self):
        return {
            "sid": self.active_song.sid,
            "pause": self.active_song.pause,
            "time": self.active_song.time,
            "volume": self.active_song.volume,
        }
