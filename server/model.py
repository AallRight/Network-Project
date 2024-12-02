from data.song import Song
from data.waitlist import Waitlist
from data.active_song import ActiveSong
from data.mlibrary import MLibrary
from server.audio_server import AudioServer

from typing import *

from proto.client_command_pb2 import ClientCommand
from proto.client_command_executor import ClientCommandExecutor

class Model:
    def __init__(self, db_path: str, music_path: str):
        self.mlibrary = MLibrary(db_path, music_path)
        self.waitlist = Waitlist(db_path)
        self.active_song = ActiveSong()
        self.audio_server = AudioServer(self.on_finish)
        self.executor = ClientCommandExecutor(self)
    
    def execute(self, client_command: ClientCommand):
        try:
            return self.executor.execute(client_command)
        except Exception as e:
            raise Exception(f"Failed to execute: {client_command}") from e

    def waitlist_add(self, sid: int):
        song = self.mlibrary.fetch_songs_by_ids([sid])[0]
        if song == None:
            raise Exception(f"Song (sid {sid}) not found.")
        self.waitlist.add(song)
    
    def waitlist_move(self, wid: int, offset: int):
        self.waitlist.move(wid, offset)

    def waitlist_delete(self, wid: int):
        self.waitlist.delete(wid)
    
    def play(self, sid: int):
        song = self.mlibrary.fetch_songs_by_ids([sid])[0]
        if song == None:
            raise Exception(f"Song (sid {sid}) not found.")
        time_stamp = self.audio_server.play(song.path)
        self.active_song.play(song, time_stamp)

    def pause(self):
        time = self.audio_server.pause()
        self.active_song.pause(time)

    def jump(self, time: int):
        is_pause, time = self.audio_server.jump(time)
        if is_pause:
            self.active_song.pause(time)
        else:
            self.active_song.play(self.active_song.song, time)

    def adjust_volume(self, volume: int):
        self.audio_server.adjust_volume(volume)
        self.active_song.adjust_volume(volume)

    def get_waitlist(self) -> list[Song]:
        return self.waitlist.get_song_list()
    
    def get_mlibrary(self, page: int)-> list[Optional[Song]]:
        sids = range(1 + (page - 1) * 20, 21 + (page - 1) * 20)
        return self.mlibrary.fetch_songs_by_ids(sids)
    
    def get_active_song(self)-> ActiveSong:
        return self.active_song
    
    def on_finish(self):
        pass

