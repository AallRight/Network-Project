import sqlite3
DB_DIR = "./cache/mlibrary"
DB_PATH = f"{DB_DIR}/songs.db"
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

    if results:
        id_list = [row[0] for row in results]
        # 测试能否返回正确的 ID 列表
        # print(id_list)
        return id_list
    else :
        return []

    # 打印查询结果
    if results:
        print(f"Found {len(results)} results for '{keyword}':")
        for row in results:
            print(f"ID: {row[0]}, Title: {row[1]}, Artist: {row[2]}, Album: {row[3]}, Length: {row[4]:.2f}s, Sample Rate: {row[5]} Hz")
    else:
        print(f"No results found for '{keyword}'.")
def search_songs_by_title(keyword):
    """根据关键字模糊搜索歌名和歌手"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 模糊查询歌名和歌手
    query = """
    SELECT id, title, artist, album, track_length, sample_rate 
    FROM songs
    WHERE title LIKE ?
    """
    cursor.execute(query, (f"%{keyword}%",))
    results = cursor.fetchall()
    conn.close()
    
    return results
    if results:
        id_list = [row[0] for row in results]
        # 测试能否返回正确的 ID 列表
        # print(id_list)
        return id_list
    else :
        return []
    
    

    # 打印查询结果
    if results:
        print(f"Found {len(results)} results for '{keyword}':")
        for row in results:
            print(f"ID: {row[0]}, Title: {row[1]}, Artist: {row[2]}, Album: {row[3]}, Length: {row[4]:.2f}s, Sample Rate: {row[5]} Hz")
    else:
        print(f"No results found for '{keyword}'.")
def search_songs_by_artist(keyword):
    """根据关键字模糊搜索歌名和歌手"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 模糊查询歌名和歌手
    query = """
    SELECT id, title, artist, album, track_length, sample_rate 
    FROM songs
    WHERE artist LIKE ?
    """
    cursor.execute(query, (f"%{keyword}%",))
    results = cursor.fetchall()
    conn.close()

    return results
    if results:
        id_list = [row[0] for row in results]
        # 测试能否返回正确的 ID 列表
        # print(id_list)
        return id_list
    else :
        return []

    # 打印查询结果
    if results:
        print(f"Found {len(results)} results for '{keyword}':")
        for row in results:
            print(f"ID: {row[0]}, Title: {row[1]}, Artist: {row[2]}, Album: {row[3]}, Length: {row[4]:.2f}s, Sample Rate: {row[5]} Hz")
    else:
        print(f"No results found for '{keyword}'.")

if __name__ == "__main__":
    # 测试模糊搜索
    keyword = input("Enter a keyword to search (by title or artist): ")
    keyword = keyword.replace(" ", "")
    search_songs_by_keyword(keyword)
    keyword1 = input("Enter a keyword to search (by title): ")
    search_songs_by_title(keyword1)
    keyword2 = input("Enter a keyword to search (by artist): ")
    search_songs_by_artist(keyword2)
