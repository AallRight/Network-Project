import sqlite3

# 数据库文件路径
DB_DIR = "./cache/mlibrary"
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

def fetch_songs_by_ids(song_ids):
    """根据 ID 列表提取对应的歌曲信息"""
    if not song_ids:
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 构建查询条件（使用 IN 子句查找多个 ID）
    query = f"SELECT * FROM songs WHERE id IN ({','.join('?' for _ in song_ids)})"
    cursor.execute(query, song_ids)
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

    # 假设你有一个 ID 列表
    id_list = [1, 2, 3]  # 例如，想查询 ID 为 1, 2, 3 的歌曲信息
    songs_by_ids = fetch_songs_by_ids(id_list)
    print_songs_table(songs_by_ids)
