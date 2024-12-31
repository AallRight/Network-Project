from data.song import Song
from data.waitlist import Waitlist
from data.active_song import ActiveSong
from data.mlibrary import MLibrary
from server.audio_backend import AudioBackend

from typing import *

from proto.message import ClientCommand, ClientQuery
from proto.binder import HandlerBinder
from server.builders import make_downlink_message_active_song, make_downlink_message_mlibrary, make_downlink_message_waitlist


class CommandService:
    def __init__(self, mlibrary: MLibrary, waitlist: Waitlist, active_song: ActiveSong, audio_backend: AudioBackend):
        self.mlibrary = mlibrary
        self.waitlist = waitlist
        self.active_song = active_song

        self.audio_backend = audio_backend
        self.handler = HandlerBinder(message_type=ClientCommand, oneof_field="command", obj=self)

    def execute(self, client_command: ClientCommand):
        try:
            return self.handler.handle(client_command)
        except Exception as e:
            raise Exception(f"Failed to execute client command. (command: >>> {client_command} <<<)") from e

    def waitlist_add(self, sid: int):
        song = self.mlibrary.get_songs_by_ids([sid])[0]
        if song == None:
            raise Exception(f"Song (sid {sid}) not found.")
        self.waitlist.add(song)
        return make_downlink_message_waitlist(self.waitlist),
    
    def waitlist_move(self, wid: int, offset: int):
        self.waitlist.move(wid, offset)
        return make_downlink_message_waitlist(self.waitlist),

    def waitlist_delete(self, wid: int):
        self.waitlist.delete(wid)
        return make_downlink_message_waitlist(self.waitlist),
    
    def play(self, sid: int, time: int):
        song = self.mlibrary.get_songs_by_ids([sid])[0]
        if song == None:
            raise Exception(f"Song (sid {sid}) not found.")
        time_stamp = self.audio_backend.play(song.path, time, song.track_length)
        self.active_song.play(song, time_stamp)
        return make_downlink_message_active_song(self.active_song),
    
    def play_next(self):
        song = self.waitlist.get_song(1)
        if song is not None:
            time_stamp = self.audio_backend.play(song.path, 0, song.track_length)
            self.active_song.play(song, time_stamp)
            self.waitlist.delete(1)
        return (make_downlink_message_active_song(self.active_song),
                make_downlink_message_waitlist(self.waitlist))
        
    def pause(self):
        time = self.audio_backend.pause()
        self.active_song.pause(time)
        return make_downlink_message_active_song(self.active_song),

    def jump(self, time: int):
        is_pause, time = self.audio_backend.jump(time)
        if is_pause:
            self.active_song.pause(time)
        else:
            self.active_song.play(self.active_song.song, time)
        return make_downlink_message_active_song(self.active_song),

    def adjust_volume(self, volume: int):
        self.audio_backend.set_volume(volume)
        self.active_song.set_volume(volume)
        return make_downlink_message_active_song(self.active_song),


class QueryService:
    def __init__(self, mlibrary: MLibrary, waitlist: Waitlist, active_song: ActiveSong):
        self.mlibrary = mlibrary
        self.waitlist = waitlist
        self.active_song = active_song

        self.handler = HandlerBinder(message_type=ClientQuery, oneof_field="query", obj=self)
    
    def get_waitlist(self):
        return make_downlink_message_waitlist(self.waitlist),
    
    def get_mlibrary(self, page: int):
        return make_downlink_message_mlibrary(self.mlibrary, page),
    
    def get_active_song(self):
        return make_downlink_message_active_song(self.active_song),
    
    def execute(self, client_query: ClientQuery):
        try:
            return self.handler.handle(client_query)
        except Exception as e:
            raise Exception(f"Failed to execute client query. (query: >>> {client_query} <<<)") from e
