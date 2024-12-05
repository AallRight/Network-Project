from data.song import Song
from data.waitlist import Waitlist
from data.active_song import ActiveSong
from data.mlibrary import MLibrary
from server.audio_server import AudioServer

from typing import *
import uuid

from proto.message import ClientCommand, ClientQuery, DownlinkMessage
from proto.binder import HandlerBinder

def make_downlink_message_waitlist(waitlist: Waitlist):
    message = DownlinkMessage()
    song_list = waitlist.get_song_list()
    song_str_list = [song.serialize() for song in song_list]
    message.waitlist.songs.extend(song_str_list)
    return message

def make_downlink_message_mlibrary(mlibrary: MLibrary, page: int):
    message = DownlinkMessage()
    message.mlibrary.page = page
    message.mlibrary.count = mlibrary.get_num_songs()
    sid_range = list(range((page - 1) * 10 + 1, page * 10 + 1))
    song_list = mlibrary.get_songs_by_ids(sid_range)
    song_str_list = [song.serialize() for song in song_list if song is not None]
    message.mlibrary.songs.extend(song_str_list)
    return message

def make_downlink_message_active_song(active_song: ActiveSong):
    message = DownlinkMessage()
    message.active_song.active_song = active_song.serialize()
    return message


class CommandService:
    def __init__(self, mlibrary: MLibrary, waitlist: Waitlist, active_song: ActiveSong):
        self.mlibrary = mlibrary
        self.waitlist = waitlist
        self.active_song = active_song

        self.audio_server = AudioServer()
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
        return make_downlink_message_waitlist(self.waitlist)
    
    def waitlist_move(self, wid: int, offset: int):
        self.waitlist.move(wid, offset)
        return make_downlink_message_waitlist(self.waitlist)

    def waitlist_delete(self, wid: int):
        self.waitlist.delete(wid)
        return make_downlink_message_waitlist(self.waitlist)
    
    def play(self, sid: int, time: int):
        song = self.mlibrary.get_songs_by_ids([sid])[0]
        if song == None:
            raise Exception(f"Song (sid {sid}) not found.")
        time_stamp = self.audio_server.play(song.path, time)
        self.active_song.play(song, time_stamp)
        return make_downlink_message_active_song(self.active_song)
    
    def play_next(self):
        song = self.waitlist.get_song(1)
        if song is not None:
            time_stamp = self.audio_server.play(song.path, 0)
            self.active_song.play(song, time_stamp)
        return make_downlink_message_active_song(self.active_song)
        
    def pause(self):
        time = self.audio_server.pause()
        self.active_song.pause(time)
        return make_downlink_message_active_song(self.active_song)

    def jump(self, time: int):
        is_pause, time = self.audio_server.jump(time)
        if is_pause:
            self.active_song.pause(time)
        else:
            self.active_song.play(self.active_song.song, time)
        return make_downlink_message_active_song(self.active_song)

    def adjust_volume(self, volume: int):
        self.audio_server.set_volume(volume)
        self.active_song.set_volume(volume)
        return make_downlink_message_active_song(self.active_song)


class QueryService:
    def __init__(self, mlibrary: MLibrary, waitlist: Waitlist, active_song: ActiveSong):
        self.mlibrary = mlibrary
        self.waitlist = waitlist
        self.active_song = active_song

        self.handler = HandlerBinder(message_type=ClientQuery, oneof_field="query", obj=self)
    
    def get_waitlist(self):
        return make_downlink_message_waitlist(self.waitlist)
    
    def get_mlibrary(self, page: int):
        return make_downlink_message_mlibrary(self.mlibrary, page)
    
    def get_active_song(self):
        return make_downlink_message_active_song(self.active_song)
    
    def execute(self, client_query: ClientQuery):
        try:
            return self.handler.handle(client_query)
        except Exception as e:
            raise Exception(f"Failed to execute client query. (query: >>> {client_query} <<<)") from e
