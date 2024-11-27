import wait_list_0 as wl
import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
parent_dir += "\mlibrary"
sys.path.append(parent_dir)
# # 添加上级目录到模块搜索路径
# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
# sys.path.append(parent_dir)
print("sys.path:")
for path in sys.path:
    print(path)
# 现在可以导入模块
import mlibrary.mlibrary_api_0 as mla


# from ..mlibrary import mlibrary_api_0 as mla

if __name__ == "__main__":
    song_data = mla.mlibrary_get_data([4,7,8])
    song_list = [wl.Song(*song) for song in song_data]
    for songs in song_list:
        print(songs)
    wait_list = wl.WaitList()
    for song in song_list:
        wait_list.add(song)
    for song in song_list:
        wait_list.add(song)
    for song in song_list:
        wait_list.add(song)
    db_path = './cache/wait_list/tem_song_list.db'
    wait_list.store(db_path)
    print(wait_list.get_idlist())
    new_wait_list = wl.WaitList()
    new_wait_list.load(db_path)
    print(new_wait_list.get_idlist())
    print(new_wait_list.get_list())
    # wait_list.add(1)
    # wait_list.add(2)
    # wait_list.add(3)
    # wait_list.add(4)
    # wait_list.add(5)
    # wait_list.add(6)
    # wait_list.add(7)
    # wait_list.add(4)
    print(wait_list.get_idlist())
    wait_list.move(2, 1)
    print(wait_list.get_idlist())
    wait_list.delete(3)
    print(wait_list.get_idlist())
    wait_list.move(3,6)
    print(wait_list.get_idlist())
    wait_list.move(3,-10)
    print(wait_list.get_idlist())
    wait_list.move_first(6)
    print(wait_list.get_idlist())