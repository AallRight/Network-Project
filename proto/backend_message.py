# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: backend_message.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x62\x61\x63kend_message.proto\"\xf4\x02\n\x12\x41udioServerCommand\x12)\n\x0fload_music_file\x18\x01 \x01(\x0b\x32\x0e.LoadMusicFileH\x00\x12 \n\nplay_music\x18\x02 \x01(\x0b\x32\n.PlayMusicH\x00\x12\"\n\x0bpause_music\x18\x03 \x01(\x0b\x32\x0b.PauseMusicH\x00\x12\x33\n\x14\x61\x64just_playback_time\x18\x04 \x01(\x0b\x32\x13.AdjustPlaybackTimeH\x00\x12-\n\radjust_volume\x18\x05 \x01(\x0b\x32\x14.BackendAdjustVolumeH\x00\x12?\n\x1astart_microphone_recording\x18\x06 \x01(\x0b\x32\x19.StartMicrophoneRecordingH\x00\x12=\n\x19stop_microphone_recording\x18\x07 \x01(\x0b\x32\x18.StopMicrophoneRecordingH\x00\x42\t\n\x07\x63ommand\"\"\n\rLoadMusicFile\x12\x11\n\tfile_path\x18\x01 \x01(\t\"\x1c\n\tPlayMusic\x12\x0f\n\x07\x61t_time\x18\x01 \x01(\x03\"\x0c\n\nPauseMusic\")\n\x12\x41\x64justPlaybackTime\x12\x13\n\x0btime_offset\x18\x01 \x01(\x03\"B\n\x13\x42\x61\x63kendAdjustVolume\x12\x14\n\x0cvolume_delta\x18\x01 \x01(\x03\x12\x15\n\ris_microphone\x18\x02 \x01(\x08\"\x1a\n\x18StartMicrophoneRecording\"\x19\n\x17StopMicrophoneRecordingb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'backend_message_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _AUDIOSERVERCOMMAND._serialized_start=26
  _AUDIOSERVERCOMMAND._serialized_end=398
  _LOADMUSICFILE._serialized_start=400
  _LOADMUSICFILE._serialized_end=434
  _PLAYMUSIC._serialized_start=436
  _PLAYMUSIC._serialized_end=464
  _PAUSEMUSIC._serialized_start=466
  _PAUSEMUSIC._serialized_end=478
  _ADJUSTPLAYBACKTIME._serialized_start=480
  _ADJUSTPLAYBACKTIME._serialized_end=521
  _BACKENDADJUSTVOLUME._serialized_start=523
  _BACKENDADJUSTVOLUME._serialized_end=589
  _STARTMICROPHONERECORDING._serialized_start=591
  _STARTMICROPHONERECORDING._serialized_end=617
  _STOPMICROPHONERECORDING._serialized_start=619
  _STOPMICROPHONERECORDING._serialized_end=644
# @@protoc_insertion_point(module_scope)
