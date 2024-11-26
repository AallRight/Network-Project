import os
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.easyid3 import EasyID3
from prettytable import PrettyTable

def get_audio_info(directory):
    """获取目录下所有 MP3 和 OGA 文件的信息并返回表格数据"""
    table = PrettyTable()
    table.field_names = ["SID", "PATH", "TITLE", "ARTIST", "ALBUM", "TRACK_LENGTH", "SAMPLE_RATE"]

    sid = 1  # 唯一歌曲编号
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".mp3", ".oga")):
                file_path = os.path.join(root, file)

                try:
                    # 检测文件类型并提取信息
                    if file.endswith(".mp3"):
                        audio = MP3(file_path, ID3=EasyID3)
                        track_length = audio.info.length
                        sample_rate = audio.info.sample_rate
                    elif file.endswith(".oga"):
                        audio = OggVorbis(file_path)
                        track_length = audio.info.length
                        sample_rate = audio.info.sample_rate

                    # 获取元数据
                    title = audio.get("title", ["Unknown"])[0]
                    artist = audio.get("artist", ["Unknown"])[0]
                    album = audio.get("album", ["Unknown"])[0]

                    # 添加到表格
                    table.add_row([sid, file_path, title, artist, album, f"{track_length:.2f}s", f"{sample_rate} Hz"])
                    sid += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    return table

if __name__ == "__main__":
    # 指定目标目录
    target_directory = "./data/music_file"

    # 获取音频文件信息并打印表格
    audio_table = get_audio_info(target_directory)
    print(audio_table)
