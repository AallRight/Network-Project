from typing import *
import traceback
import threading
import queue
from flask_socketio import SocketIO

from data.song import Song
from data.waitlist import Waitlist
from data.active_song import ActiveSong
from data.mlibrary import MLibrary

from server.service import CommandService, QueryService
from server.audio_backend import AudioBackend
from proto.message import UplinkMessage, DownlinkMessage
from server.constant import *

from server.builders import make_uplink_message_play_next

class Controller:
    def __init__(self, socketio: SocketIO, users_manager: "UsersManager", db_path: str, music_path: str, audio_server_url: str):
        waitlist = Waitlist(db_path)
        mlibrary = MLibrary(db_path, music_path)
        active_song = ActiveSong()
        audio_backend = AudioBackend(lambda: self.put_uplink_message(make_uplink_message_play_next()), audio_server_url)

        self.command_service = CommandService(mlibrary, waitlist, active_song, audio_backend)
        self.query_service = QueryService(mlibrary, waitlist, active_song)
        self.command_id = ESCAPE_COMMAND_ID

        self.uplink_message_queue = queue.Queue()
        self.downlink_message_queue = queue.Queue()
        self.socketio = socketio
        self.users_manager = users_manager

    def start(self):
        threading.Thread(target=self.__uplink_message_loop, daemon=True).start()
        threading.Thread(target=self.__downlink_message_loop, daemon=True).start()

    @staticmethod
    def parse_uplink_message(message: str):
        uplink_message = UplinkMessage()
        uplink_message.ParseFromString(message)
        return uplink_message

    def put_uplink_message(self, message: UplinkMessage):
        self.uplink_message_queue.put(message)

    def __uplink_message_loop(self):
        while True:
            uplink_message = self.uplink_message_queue.get()
            self.__handle(uplink_message)
    
    def __downlink_message_loop(self):
        while True:
            to_user, downlink_message = self.downlink_message_queue.get()
            downlink_message_str = downlink_message.SerializeToString()
            if to_user == ALL_USER_ID:
                self.socketio.emit('downlink_message', downlink_message_str)  # broadcast
                continue

            if to_user == ESCAPE_USER_ID:
                continue
            
            sid = self.users_manager.get_sid(to_user)
            if sid is not None:
                self.socketio.emit('downlink_message', downlink_message_str, to=sid)
            else:
                print(f"user_id {to_user} is not found.")

    def __handle(self, uplink_message: UplinkMessage) -> Tuple[int, DownlinkMessage]:
        try:
            payload = uplink_message.WhichOneof("payload")
            if payload == "client_command":
                client_command = uplink_message.client_command
                if client_command.command_id != self.command_id + 1 and client_command.command_id != ESCAPE_COMMAND_ID:
                    raise Exception(f"Wrong command_id. (Expected {self.command_id + 1})")
                downlink_messages = self.command_service.execute(uplink_message.client_command)
                self.command_id += 1
                for downlink_message in downlink_messages:
                    downlink_message.command_id = self.command_id
                    self.downlink_message_queue.put((ALL_USER_ID, downlink_message))

            elif payload == "client_query":
                downlink_messages = self.query_service.execute(uplink_message.client_query)
                for downlink_message in downlink_messages:
                    downlink_message.command_id = self.command_id
                    self.downlink_message_queue.put((uplink_message.user_id, downlink_message))

            else:
                raise Exception(f"Unrecognized payload. (message: >>> {uplink_message} <<<)")
            
        except Exception as e:
            downlink_message = DownlinkMessage()
            downlink_message.error.error = str(traceback.format_exc() + str(e))
            self.downlink_message_queue.put((uplink_message.user_id, downlink_message))
        
            
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
        with self.user_lock:
            return self.user_id_to_sid.get(user_id, None)