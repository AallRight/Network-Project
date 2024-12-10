from data.song import Song
from data.waitlist import Waitlist
from data.active_song import ActiveSong
from data.mlibrary import MLibrary

from server.constant import *
from proto.message import UplinkMessage, ClientCommand, PlayNext
from proto.message import ClientCommand, DownlinkMessage, WaitlistProto, MLibraryProto, ActiveSongProto


def make_downlink_message_waitlist(waitlist: Waitlist):
    song_list = waitlist.get_song_list()
    song_str_list = [song.serialize() for song in song_list]
    return DownlinkMessage(
        waitlist=WaitlistProto(
            songs=song_str_list
        )
    )

def make_downlink_message_mlibrary(mlibrary: MLibrary, page: int):
    sid_range = list(range((page - 1) * 10 + 1, page * 10 + 1))
    song_list = mlibrary.get_songs_by_ids(sid_range)
    song_str_list = [song.serialize() for song in song_list if song is not None]
    return DownlinkMessage(
        mlibrary=MLibraryProto(
            page=page,
            count=mlibrary.get_num_songs(),
            songs=song_str_list
        )
    )

def make_downlink_message_active_song(active_song: ActiveSong):
    return DownlinkMessage(
        active_song=ActiveSongProto(
            active_song=active_song.serialize()
        )
    )

def make_uplink_message_play_next():
    return UplinkMessage(
        user_id=ESCAPE_USER_ID,
        client_command=ClientCommand(
            command_id=ESCAPE_COMMAND_ID,
            play_next=PlayNext()
        )
    )