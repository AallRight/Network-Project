import sys
import os 
# import active_song.active_song as asong
# import active_song.active_song_autotime as asong_auto
import active_song_autotime as asong_auto
import time

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    
sys.path.append(parent_dir)
mlibrary_dir = parent_dir + "\mlibrary"
sys.path.append(mlibrary_dir)
wait_list_dir = parent_dir + "\wait_list"
sys.path.append(wait_list_dir)
print("sys.path:")
for path in sys.path:
    print(path)

import mlibrary.mlibrary_api_0 as mla
import wait_list.wait_list_0 as wl
from wait_list.wait_list_0 import Song




if __name__ == "__main__":
    song_data = mla.mlibrary_get_data([3,5,7])
    song_list = [Song(*song) for song in song_data]
    active_song = asong_auto.ActiveSong(song_list[0])
    active_song.play(1)  # 假设开始播放歌曲
    time.sleep(2)  # 模拟歌曲播放2秒
    print(f"播放时长: {active_song.get_played_time()}秒")
    active_song.pause_song()  # 暂停播放
    time.sleep(1)  # 暂停1秒
    print(f"已播放时长（暂停后）：{active_song.get_played_time()}秒")
    active_song.play(1)  # 恢复播放
    time.sleep(1)  # 再播放1秒
    print(f"恢复播放后的时长: {active_song.get_played_time()}秒")
    