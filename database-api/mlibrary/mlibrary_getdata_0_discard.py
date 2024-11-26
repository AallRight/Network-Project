import sqlite3

# 数据库文件路径
DB_PATH = "./cache/mlibrary/songs.db"

def fetch_all_songs():
    """从数据库中提取所有歌曲信息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 查询所有信息
    query = "SELECT * FROM songs"
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()
    return results

def print_songs_table(songs):
    """以表格形式打印歌曲信息"""
    if songs:
        print(f"Found {len(songs)} songs in the database:")
        print(f"{'ID':<5} {'Title':<30} {'Artist':<20} {'Album':<20} {'Length':<10} {'Sample Rate':<10} {'Path':<40}")
        print("=" * 135)
        for song in songs:
            id, path, title, artist, album, track_length, sample_rate = song
            print(f"{id:<5} {title:<30} {artist:<20} {album:<20} {track_length:<10.2f} {sample_rate:<10} {path:<40}")
    else:
        print("No songs found in the database.")

if __name__ == "__main__":
    # 提取并打印所有歌曲信息
    songs = fetch_all_songs()
    print_songs_table(songs)
    print(songs)
