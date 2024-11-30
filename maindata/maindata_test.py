import sys
import os
import time


parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
sys.dont_write_bytecode = True

from maindata.maindata_api import MainData

if __name__ == "__main__":
    maindata = MainData(sys.argv[1], sys.argv[2])

    print("模拟前端请求歌曲库的列表")
    songs = maindata.fetch_songs_by_ids(list(range(1, 8)))
    for song in songs:
        assert song is not None, "为了测试需要，请至少放 7 首歌"
        print(song)
    
    print("模拟前端向播放列表中添加、删除、移动歌曲")
    maindata.waitlist_add(3) # [3]
    maindata.waitlist_add(5) # [3, 5]
    maindata.waitlist_add(1) # [3, 5, 1]
    maindata.waitlist_add(2) # [3, 5, 1, 2]
    maindata.waitlist_delete(1) # [5, 1, 2]
    maindata.waitlist_move(2, -1) # [1, 5, 2]
    maindata.waitlist_move(1, 2) # [5, 2, 1]
    songs = maindata.waitlist_get()
    print("WaitList:")
    for song in songs:
        print(song)

    print("模拟前端发送播放指令后，音频服务器返回播放状态")
    maindata.play(5, int(time.time() * 1000))
    maindata.waitlist_delete(1) # [1, 2]
    print(maindata.active_song)

    time.sleep(2.0)  # 模拟歌曲播放 10s

    print("模拟前端发送暂停指令后，音频服务器返回暂停状态")
    maindata.pause(2 * 1000)
    print(maindata.active_song)

    print("模拟前端调整音量为 40")
    maindata.adjust_volume(40)
    print(maindata.active_song)

    print(f"模拟前端检索歌曲库，检索词 {songs[0].artist[:2]}")
    songs = maindata.fetch_songs_by_keyword(songs[0].artist[:2])
    for song in songs:
        print(song)

    

