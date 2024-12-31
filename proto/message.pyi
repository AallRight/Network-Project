from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class ActiveSongProto(_message.Message):
    __slots__ = ["active_song"]
    ACTIVE_SONG_FIELD_NUMBER: ClassVar[int]
    active_song: str
    def __init__(self, active_song: Optional[str] = ...) -> None: ...

class AdjustVolume(_message.Message):
    __slots__ = ["volume"]
    VOLUME_FIELD_NUMBER: ClassVar[int]
    volume: int
    def __init__(self, volume: Optional[int] = ...) -> None: ...

class ClientCommand(_message.Message):
    __slots__ = ["adjust_volume", "command_id", "jump", "pause", "play", "play_next", "waitlist_add", "waitlist_delete", "waitlist_move"]
    ADJUST_VOLUME_FIELD_NUMBER: ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: ClassVar[int]
    JUMP_FIELD_NUMBER: ClassVar[int]
    PAUSE_FIELD_NUMBER: ClassVar[int]
    PLAY_FIELD_NUMBER: ClassVar[int]
    PLAY_NEXT_FIELD_NUMBER: ClassVar[int]
    WAITLIST_ADD_FIELD_NUMBER: ClassVar[int]
    WAITLIST_DELETE_FIELD_NUMBER: ClassVar[int]
    WAITLIST_MOVE_FIELD_NUMBER: ClassVar[int]
    adjust_volume: AdjustVolume
    command_id: int
    jump: Jump
    pause: Pause
    play: Play
    play_next: PlayNext
    waitlist_add: WaitlistAdd
    waitlist_delete: WaitlistDelete
    waitlist_move: WaitlistMove
    def __init__(self, command_id: Optional[int] = ..., waitlist_add: Optional[Union[WaitlistAdd, Mapping]] = ..., waitlist_move: Optional[Union[WaitlistMove, Mapping]] = ..., waitlist_delete: Optional[Union[WaitlistDelete, Mapping]] = ..., play: Optional[Union[Play, Mapping]] = ..., pause: Optional[Union[Pause, Mapping]] = ..., jump: Optional[Union[Jump, Mapping]] = ..., adjust_volume: Optional[Union[AdjustVolume, Mapping]] = ..., play_next: Optional[Union[PlayNext, Mapping]] = ...) -> None: ...

class ClientQuery(_message.Message):
    __slots__ = ["get_active_song", "get_mlibrary", "get_waitlist"]
    GET_ACTIVE_SONG_FIELD_NUMBER: ClassVar[int]
    GET_MLIBRARY_FIELD_NUMBER: ClassVar[int]
    GET_WAITLIST_FIELD_NUMBER: ClassVar[int]
    get_active_song: GetActiveSong
    get_mlibrary: GetMLibrary
    get_waitlist: GetWaitlist
    def __init__(self, get_waitlist: Optional[Union[GetWaitlist, Mapping]] = ..., get_mlibrary: Optional[Union[GetMLibrary, Mapping]] = ..., get_active_song: Optional[Union[GetActiveSong, Mapping]] = ...) -> None: ...

class DownlinkMessage(_message.Message):
    __slots__ = ["active_song", "command_id", "error", "mlibrary", "waitlist"]
    ACTIVE_SONG_FIELD_NUMBER: ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: ClassVar[int]
    ERROR_FIELD_NUMBER: ClassVar[int]
    MLIBRARY_FIELD_NUMBER: ClassVar[int]
    WAITLIST_FIELD_NUMBER: ClassVar[int]
    active_song: ActiveSongProto
    command_id: int
    error: Error
    mlibrary: MLibraryProto
    waitlist: WaitlistProto
    def __init__(self, command_id: Optional[int] = ..., waitlist: Optional[Union[WaitlistProto, Mapping]] = ..., active_song: Optional[Union[ActiveSongProto, Mapping]] = ..., mlibrary: Optional[Union[MLibraryProto, Mapping]] = ..., error: Optional[Union[Error, Mapping]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ["error"]
    ERROR_FIELD_NUMBER: ClassVar[int]
    error: str
    def __init__(self, error: Optional[str] = ...) -> None: ...

class GetActiveSong(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetMLibrary(_message.Message):
    __slots__ = ["page"]
    PAGE_FIELD_NUMBER: ClassVar[int]
    page: int
    def __init__(self, page: Optional[int] = ...) -> None: ...

class GetWaitlist(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Jump(_message.Message):
    __slots__ = ["time"]
    TIME_FIELD_NUMBER: ClassVar[int]
    time: int
    def __init__(self, time: Optional[int] = ...) -> None: ...

class MLibraryProto(_message.Message):
    __slots__ = ["count", "page", "songs"]
    COUNT_FIELD_NUMBER: ClassVar[int]
    PAGE_FIELD_NUMBER: ClassVar[int]
    SONGS_FIELD_NUMBER: ClassVar[int]
    count: int
    page: int
    songs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, page: Optional[int] = ..., count: Optional[int] = ..., songs: Optional[Iterable[str]] = ...) -> None: ...

class Pause(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Play(_message.Message):
    __slots__ = ["sid", "time"]
    SID_FIELD_NUMBER: ClassVar[int]
    TIME_FIELD_NUMBER: ClassVar[int]
    sid: int
    time: int
    def __init__(self, sid: Optional[int] = ..., time: Optional[int] = ...) -> None: ...

class PlayNext(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class UplinkMessage(_message.Message):
    __slots__ = ["client_command", "client_query", "user_id"]
    CLIENT_COMMAND_FIELD_NUMBER: ClassVar[int]
    CLIENT_QUERY_FIELD_NUMBER: ClassVar[int]
    USER_ID_FIELD_NUMBER: ClassVar[int]
    client_command: ClientCommand
    client_query: ClientQuery
    user_id: int
    def __init__(self, user_id: Optional[int] = ..., client_command: Optional[Union[ClientCommand, Mapping]] = ..., client_query: Optional[Union[ClientQuery, Mapping]] = ...) -> None: ...

class WaitlistAdd(_message.Message):
    __slots__ = ["sid"]
    SID_FIELD_NUMBER: ClassVar[int]
    sid: int
    def __init__(self, sid: Optional[int] = ...) -> None: ...

class WaitlistDelete(_message.Message):
    __slots__ = ["wid"]
    WID_FIELD_NUMBER: ClassVar[int]
    wid: int
    def __init__(self, wid: Optional[int] = ...) -> None: ...

class WaitlistMove(_message.Message):
    __slots__ = ["offset", "wid"]
    OFFSET_FIELD_NUMBER: ClassVar[int]
    WID_FIELD_NUMBER: ClassVar[int]
    offset: int
    wid: int
    def __init__(self, wid: Optional[int] = ..., offset: Optional[int] = ...) -> None: ...

class WaitlistProto(_message.Message):
    __slots__ = ["songs"]
    SONGS_FIELD_NUMBER: ClassVar[int]
    songs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, songs: Optional[Iterable[str]] = ...) -> None: ...
