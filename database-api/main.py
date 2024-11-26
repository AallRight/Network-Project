from main_data import MainData

# 初始化
main_data = MainData()

# 添加歌曲到 Library
main_data.add_to_library(1, "/path/song1.mp3", "Song 1", "Artist 1", "Album 1", 300, 44100)
main_data.add_to_library(2, "/path/song2.mp3", "Song 2", "Artist 2", "Album 2", 200, 44100)

# 添加到等待列表
main_data.wait_list_add(1)
main_data.wait_list_add(2)

# 播放当前歌曲
main_data.active_song_play()
print("Active Song:", main_data.get_active_song_status())

# 调整音量
main_data.active_song_adjust_vol(80)
print("Adjusted Volume:", main_data.get_active_song_status()["volume"])

# 暂停歌曲
main_data.active_song_pause()
print("Paused Song Status:", main_data.get_active_song_status())
