from typing import *
import traceback
import threading

from data.song import Song
from data.waitlist import Waitlist
from data.active_song import ActiveSong
from data.mlibrary import MLibrary

from server.service import CommandService, QueryService
from proto.message import UplinkMessage, DownlinkMessage

INIT_COMMAND_ID = 1
ESCAPE_COMMAND_ID = 0
INIT_USER_ID = 1
ESCAPE_USER_ID = 0

class Controller:
    def __init__(self, db_path: str, music_path: str):
        waitlist = Waitlist(db_path)
        mlibrary = MLibrary(db_path, music_path)
        active_song = ActiveSong()

        self.command_service = CommandService(mlibrary, waitlist, active_song)
        self.query_service = QueryService(mlibrary, waitlist, active_song)
        self.command_id = ESCAPE_COMMAND_ID

    def handle(self, uplink_message_str: str) -> Tuple[str, Optional[int]]:
        uplink_message = UplinkMessage()
        downlink_message = DownlinkMessage()
        to_user = None
        try:
            uplink_message.ParseFromString(uplink_message_str)
            payload = uplink_message.WhichOneof("payload")
            if payload == "client_command":
                client_command = uplink_message.client_command
                if client_command.command_id != self.command_id + 1 and client_command.command_id != ESCAPE_COMMAND_ID:
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
                raise Exception(f"Unrecognized payload. message: >>> {uplink_message} <<<")
            
        except Exception as e:
            downlink_message.error.error = str(traceback.format_exc() + str(e))
            to_user = uplink_message.user_id

        downlink_message_str = downlink_message.SerializeToString()
        return downlink_message_str, to_user

            
class UsersManager:
    def __init__(self):
        self.user_lock = threading.Lock()
        self.user_id_counter = INIT_USER_ID
        self.user_id_to_sid = {}
        self.sid_to_user_id = {}

    def allocate(self, sid: str) -> int:
        with self.user_lock:
            user_id = self.user_id_counter
            self.user_id_to_sid[user_id] = sid
            self.sid_to_user_id[sid] = user_id
            self.user_id_counter += 1
        return user_id
    
    def deallocate(self, sid: str) -> int:
        with self.user_lock:
            user_id = self.sid_to_user_id[sid]
            del self.sid_to_user_id[sid]
            del self.user_id_to_sid[user_id]
        return user_id
    
    def get_sid(self, user_id: int) -> Optional[str]:
        return self.user_id_to_sid.get(user_id, None)