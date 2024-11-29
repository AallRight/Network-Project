import os
import time
import pygame
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
from prettytable import PrettyTable

# ActiveSong 类
class ActiveSong:
    """当前播放的歌曲"""
    def __init__(self, song_data=None):
        self.sid = None
        self.song_data = song_data
        self.pause = True
        self.time = 0.0  # 播放时间
        self.time_stamp = None
        self.volume = 50  # 默认音量

        if song_data:
            self.sid = song_data.id
            self.song_data = song_data

    def play(self, song_file):
        """开始播放歌曲"""
        if song_file.endswith((".mp3", ".flac")):
            pygame.mixer.init()  # 初始化pygame的音频系统
            pygame.mixer.music.load(song_file)  # 加载音乐文件
            pygame.mixer.music.set_volume(self.volume / 100.0)  # 设置音量
            pygame.mixer.music.play(loops=0, start=self.time)  # 播放并从当前时间开始
        elif song_file.endswith((".ogg", ".oga")):
            # 转换 .ogg 或 .oga 文件为临时的 wav 文件
            temp_file = "temp_song.wav"
            audio = AudioSegment.from_file(song_file)
            audio.export(temp_file, format="wav")
            pygame.mixer.init()  # 初始化pygame的音频系统
            pygame.mixer.music.load(temp_file)  # 加载转换后的 wav 文件
            pygame.mixer.music.set_volume(self.volume / 100.0)  # 设置音量
            pygame.mixer.music.play(loops=0, start=self.time)  # 播放并从当前时间开始
            os.remove(temp_file)  # 删除临时文件

        self.pause = False
        self.time_stamp = time.time()  # 记录开始播放的时间

    def pause_song(self):
        """暂停歌曲播放"""
        pygame.mixer.music.pause()
        self.pause = True
        self.time += time.time() - self.time_stamp  # 更新播放时间
        self.time_stamp = None

    def resume_song(self):
        """恢复歌曲播放"""
        pygame.mixer.music.unpause()
        self.time_stamp = time.time()  # 记录恢复播放的时间
        self.pause = False

    def adjust_vol(self, volume):
        """调整音量"""
        self.volume = max(0, min(100, volume))  # 限制音量范围为0~100
        pygame.mixer.music.set_volume(self.volume / 100.0)

    def update_time(self):
        """更新播放时间"""
        if not self.pause:
            # 计算当前播放时间，更新 ActiveSong 中的时间
            self.time = time.time() - self.time_stamp + self.time

    def stop(self):
        """停止播放"""
        pygame.mixer.music.stop()
        self.time = 0.0
        self.time_stamp = None

    def get_current_time(self):
        """获取当前播放时间"""
        return self.time

# 获取音频文件信息并存储到数据库
def get_audio_info(directory):
    """获取目录下所有 MP3 和 OGA 文件的信息并存储到数据库"""
    table = PrettyTable()
    table.field_names = ["SID", "PATH", "TITLE", "ARTIST", "ALBUM", "TRACK_LENGTH", "SAMPLE_RATE"]
    sid = 1  # 唯一歌曲编号
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".mp3", ".oga", ".ogg", ".flac")):
                file_path = os.path.join(root, file)

                try:
                    # 检测文件类型并提取信息
                    if file.endswith(".mp3"):
                        audio = MP3(file_path, ID3=EasyID3)
                        track_length = audio.info.length
                        sample_rate = audio.info.sample_rate
                    elif file.endswith(".flac"):
                        audio = FLAC(file_path)
                        track_length = audio.info.length
                        sample_rate = audio.info.sample_rate
                    elif file.endswith(".oga") or file.endswith(".ogg"):
                        audio = OggVorbis(file_path)
                        track_length = audio.info.length
                        sample_rate = audio.info.sample_rate

                    # 获取元数据
                    title = audio.get("title", ["Unknown"])[0]
                    artist = audio.get("artist", ["Unknown"])[0]
                    album = audio.get("album", ["Unknown"])[0]

                    # 插入到数据库
                    table.add_row([sid, file_path, title, artist, album, f"{track_length:.2f}s", f"{sample_rate} Hz"])
                    sid += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return table

# 示例用法
if __name__ == "__main__":
    song_file = "data\music_file\陈慧娴+-+情意结.flac"  # 替换为实际的文件路径
    active_song = ActiveSong()  # 创建 ActiveSong 实例

    # 播放音乐
    active_song.play(song_file)
    print("Music is playing...")

    # 模拟播放一段时间
    time.sleep(5)  # 假设播放了5秒钟

    # 获取当前播放时间
    active_song.update_time()  # 更新播放时间
    print(f"Current Time: {active_song.get_current_time()} seconds")

    # 暂停播放
    active_song.pause_song()
    print("Music paused.")

    time.sleep(2)  # 暂停2秒

    # 恢复播放
    active_song.resume_song()
    print("Music resumed.")

    time.sleep(5)  # 播放5秒钟

    # 获取当前播放时间
    active_song.update_time()
    print(f"Current Time: {active_song.get_current_time()} seconds")
    
    # 停止播放
    active_song.stop()
    print("Music stopped.")
