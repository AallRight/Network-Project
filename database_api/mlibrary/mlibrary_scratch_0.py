import os
import sqlite3
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from prettytable import PrettyTable

# 数据库文件路径
DB_DIR = "./cache/mlibrary"
DB_PATH = f"{DB_DIR}/songs.db"

def initialize_database():
    """初始化 SQLite 数据库和表"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建 songs 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 唯一歌曲编号
        path TEXT NOT NULL,                     -- 文件路径
        title TEXT NOT NULL,                    -- 歌曲名
        artist TEXT,                            -- 歌手
        album TEXT,                             -- 专辑
        track_length REAL,                      -- 歌曲时长
        sample_rate INTEGER                     -- 采样率
    )
    """)
    conn.commit()
    conn.close()

def insert_audio_info(path, title, artist, album, track_length, sample_rate):
    """将音频信息插入到 SQLite 数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 插入数据
    cursor.execute("""
    INSERT INTO songs (path, title, artist, album, track_length, sample_rate)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (path, title, artist, album, track_length, sample_rate))

    conn.commit()
    conn.close()

def get_audio_info(directory):
    """获取目录下所有 MP3 和 OGA 文件的信息并存储到数据库"""
    table = PrettyTable()
    table.field_names = ["SID", "PATH", "TITLE", "ARTIST", "ALBUM", "TRACK_LENGTH", "SAMPLE_RATE"]
    sid = 1  # 唯一歌曲编号
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".mp3", ".oga", ".ogg")):
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
                    elif file.endswith(".ogg"):
                        audio = OggVorbis(file_path)
                        track_length = audio.info.length
                        sample_rate = audio.info.sample_rate
                    elif file.endswith(".flac"):
                        audio = FLAC(file_path)
                        track_length = audio.info.length
                        sample_rate = audio.info.sample_rate

                    # 获取元数据
                    title = audio.get("title", ["Unknown"])[0]
                    artist = audio.get("artist", ["Unknown"])[0]
                    album = audio.get("album", ["Unknown"])[0]

                    # 插入到数据库
                    table.add_row([sid, file_path, title, artist, album, f"{track_length:.2f}s", f"{sample_rate} Hz"])
                    insert_audio_info(file_path, title, artist, album, track_length, sample_rate)
                    sid += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return table

def search_songs_by_keyword(keyword):
    """根据关键字模糊搜索歌名和歌手"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 模糊查询歌名和歌手
    query = """
    SELECT id, title, artist, album, track_length, sample_rate 
    FROM songs
    WHERE title LIKE ? OR artist LIKE ?
    """
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()

    # 打印查询结果
    if results:
        print(f"Found {len(results)} results for '{keyword}':")
        for row in results:
            print(f"ID: {row[0]}, Title: {row[1]}, Artist: {row[2]}, Album: {row[3]}, Length: {row[4]:.2f}s, Sample Rate: {row[5]} Hz")
    else:
        print(f"No results found for '{keyword}'.")

if __name__ == "__main__":
    # 初始化数据库
    initialize_database()

    # 指定目标目录
    target_directory = "./data/music_file"

    # 获取音频文件信息并存储到数据库
    print("Scanning and storing audio files...")
    audio_table = get_audio_info(target_directory)
    print(audio_table)
    print("Audio files processed and stored in database.")

    # 测试模糊搜索
    keyword = input("Enter a keyword to search (by title or artist): ")
    search_songs_by_keyword(keyword)
