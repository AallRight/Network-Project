from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class AdjustPlaybackTime(_message.Message):
    __slots__ = ["time_offset"]
    TIME_OFFSET_FIELD_NUMBER: ClassVar[int]
    time_offset: int
    def __init__(self, time_offset: Optional[int] = ...) -> None: ...

class AudioServerCommand(_message.Message):
    __slots__ = ["adjust_playback_time", "adjust_volume", "load_music_file", "pause_music", "play_music", "start_microphone_recording", "stop_microphone_recording"]
    ADJUST_PLAYBACK_TIME_FIELD_NUMBER: ClassVar[int]
    ADJUST_VOLUME_FIELD_NUMBER: ClassVar[int]
    LOAD_MUSIC_FILE_FIELD_NUMBER: ClassVar[int]
    PAUSE_MUSIC_FIELD_NUMBER: ClassVar[int]
    PLAY_MUSIC_FIELD_NUMBER: ClassVar[int]
    START_MICROPHONE_RECORDING_FIELD_NUMBER: ClassVar[int]
    STOP_MICROPHONE_RECORDING_FIELD_NUMBER: ClassVar[int]
    adjust_playback_time: AdjustPlaybackTime
    adjust_volume: BackendAdjustVolume
    load_music_file: LoadMusicFile
    pause_music: PauseMusic
    play_music: PlayMusic
    start_microphone_recording: StartMicrophoneRecording
    stop_microphone_recording: StopMicrophoneRecording
    def __init__(self, load_music_file: Optional[Union[LoadMusicFile, Mapping]] = ..., play_music: Optional[Union[PlayMusic, Mapping]] = ..., pause_music: Optional[Union[PauseMusic, Mapping]] = ..., adjust_playback_time: Optional[Union[AdjustPlaybackTime, Mapping]] = ..., adjust_volume: Optional[Union[BackendAdjustVolume, Mapping]] = ..., start_microphone_recording: Optional[Union[StartMicrophoneRecording, Mapping]] = ..., stop_microphone_recording: Optional[Union[StopMicrophoneRecording, Mapping]] = ...) -> None: ...

class BackendAdjustVolume(_message.Message):
    __slots__ = ["is_microphone", "volume_delta"]
    IS_MICROPHONE_FIELD_NUMBER: ClassVar[int]
    VOLUME_DELTA_FIELD_NUMBER: ClassVar[int]
    is_microphone: bool
    volume_delta: float
    def __init__(self, volume_delta: Optional[float] = ..., is_microphone: bool = ...) -> None: ...

class LoadMusicFile(_message.Message):
    __slots__ = ["file_path"]
    FILE_PATH_FIELD_NUMBER: ClassVar[int]
    file_path: str
    def __init__(self, file_path: Optional[str] = ...) -> None: ...

class PauseMusic(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class PlayMusic(_message.Message):
    __slots__ = ["at_time"]
    AT_TIME_FIELD_NUMBER: ClassVar[int]
    at_time: int
    def __init__(self, at_time: Optional[int] = ...) -> None: ...

class StartMicrophoneRecording(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class StopMicrophoneRecording(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
