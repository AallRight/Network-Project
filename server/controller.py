from typing import *
import traceback

from data.song import Song
from data.waitlist import Waitlist
from data.active_song import ActiveSong
from data.mlibrary import MLibrary

from server.service import CommandService, QueryService
from proto.message import UplinkMessage, DownlinkMessage


class Controller:
    def __init__(self, db_path: str, music_path: str):
        waitlist = Waitlist(db_path)
        mlibrary = MLibrary(db_path, music_path)
        active_song = ActiveSong()

        self.command_service = CommandService(mlibrary, waitlist, active_song)
        self.query_service = QueryService(mlibrary, waitlist, active_song)
        self.command_id = 1

    def handle(self, uplink_message_str: str) -> Tuple[str, Optional[int]]:
        uplink_message = UplinkMessage()
        downlink_message = DownlinkMessage()
        to_user = None
        try:
            uplink_message.ParseFromString(uplink_message_str)
            payload = uplink_message.WhichOneof("payload")
            if payload == "client_command":
                client_command = uplink_message.client_command
                if client_command.command_id != self.command_id + 1:
                    raise Exception
                downlink_message = self.command_service.execute(uplink_message.client_command)
                self.command_id += 1
                downlink_message.command_id = self.command_id
                to_user = None

            elif payload == "client_query":
                downlink_message = self.query_service.execute(uplink_message.client_query)
                downlink_message.command_id = self.command_id
                to_user = uplink_message.user_id

            else:
                raise Exception(f"Unrecognized payload {payload}")
            
        except Exception as e:
            downlink_message.error.error = str(traceback.format_exc() + str(e))
            to_user = uplink_message.user_id

        downlink_message_str = downlink_message.SerializeToString()
        return downlink_message_str, to_user

            
