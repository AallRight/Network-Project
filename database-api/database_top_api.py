import os
import sys
from typing import List, Dict

import wait_list.wait_list_0


current_dir = os.path.dirname(os.path.abspath(__file__))
mlibrary_dir = os.path.join(current_dir, "mlibrary")
sys.path.append(mlibrary_dir)
wait_list_dir = os.path.join(current_dir, "wait_list")
sys.path.append(wait_list_dir)
active_song_dir = os.path.join(current_dir, "active_song")
sys.path.append(active_song_dir)
import mlibrary
import wait_list
import active_song
import active_song.active_song_0

print("sys.path:")
for path in sys.path:
    print(path)
# 内存长期存在的变量名
V_waitlist = None
V_waitlist = wait_list.wait_list_0.WaitList()

V_activesong = None
V_activesong = active_song.active_song_0.ActiveSong()


def mlibrary_exist():
    if os.path.exists(mlibrary.mlibrary_scratch_0.DB_PATH):
        return True
    else:
        return False

def mlibrary_init():
    mlibrary.mlibrary_api_0.mlibrary_initialize()

def mlibrary_search_song_by_title(title: str):
    return mlibrary.mlibrary_api_0.mlibrary_search_title(title)

def mlibrary_search_song_by_artist(artist: str):
    return mlibrary.mlibrary_api_0.mlibrary_search_artist(artist)

def mlibrary_get_data(id_list: List[int]) -> List[Dict]:
    return mlibrary.mlibrary_api_0.mlibrary_get_data(id_list)

def wait_list_add(sid: int):
    id_list = [sid]
    song_data = mlibrary.mlibrary_api_0.mlibrary_get_data(id_list)
    song_list = [wait_list.wait_list_0.Song(*song) for song in song_data]
    for song in song_list:
        V_waitlist.add(song)
    return V_waitlist.get_list()

def wait_list_move(wid: int, offset: int):
    return V_waitlist.move(wid, offset)

def wait_list_delete(wid: int) :
    return V_waitlist.delete(wid)

def active_song_adjust_vol(volume: int):
    return V_activesong.adjust_vol(volume)






if  __name__ == "__main__":
    if mlibrary_exist():
        print("数据库已存在")
    else:
        print("数据库不存在")
        mlibrary_init()
        print("数据库初始化完成")
    # mlibrary_init()
    list = mlibrary_search_song_by_title("明我")
    print(list)
    list = mlibrary_search_song_by_artist("真夜")
    print(list)

    print("这是add 1,2,1,7")
    print(wait_list_add(1))
    print(wait_list_add(2))
    print(wait_list_add(1))
    print(wait_list_add(7))

    print("这是move 3 2")
    print(wait_list_move(3, 2))
    
    print(wait_list_delete(2))

    print(active_song_adjust_vol(60))

    print("程序结束")