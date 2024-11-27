import sys
import os 
import active_song.active_song as asong

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
import wait_list.wait_list as wl



if __name__ == "__main__":
    song_data = mla.mlibrary_get_data([3,5,7])
    song_list = [wl.Song(*song) for song in song_data]
    