import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.dont_write_bytecode = True

from server.model import Model
from proto.client_command_pb2 import ClientCommand

if __name__ == "__main__":
    model = Model(sys.argv[1], sys.argv[2])

    print("\n模拟前端请求歌曲库的列表")
    songs = model.get_mlibrary(1)
    songs = list(filter(lambda song: song is not None, songs))
    assert len(songs) >= 7, "为了测试需要，请至少放 7 首歌"
    for song in songs:
        print(song)
    
    print("\n模拟前端向播放列表中添加、删除、移动歌曲")
    model.waitlist_add(3) # [3]
    model.waitlist_add(5) # [3, 5]
    model.waitlist_add(1) # [3, 5, 1]
    model.waitlist_add(2) # [3, 5, 1, 2]
    model.waitlist_delete(1) # [5, 1, 2]
    model.waitlist_move(2, -1) # [1, 5, 2]

    cm = ClientCommand()
    cm.waitlist_move.wid = 1
    cm.waitlist_move.offset = 2
    model.execute(cm) # [5, 2, 1]
    # 等效于 model.waitlist_move(1, 2) 

    songs = model.get_waitlist()
    print("WaitList:")
    for song in songs:
        print(song)

    print("\n模拟前端发送播放指令")
    model.play(5)
    print(model.active_song)

    time.sleep(2.0)  # 模拟歌曲播放 2 s

    print("\n模拟前端发送暂停指令")
    model.pause()
    print(model.active_song)

    print("\n模拟前端调整音量为 40")
    model.adjust_volume(40)
    print(model.active_song)

    # print(f"\n模拟前端检索歌曲库，检索词 {songs[0].artist[:2]}")
    # songs = model.fetch_songs_by_keyword(songs[0].artist[:2])
    # for song in songs:
    #     print(song)

    

