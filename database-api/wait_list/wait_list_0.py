import os 
import sqlite3
WAIT_LIST_DB_PATH = "./cache/wait_list/wait_list.db"
class Song:
    """表示一首歌曲的类"""
    def __init__(self, id, path, title, artist, album, track_length, sample_rate):
        self.id = id
        self.path = path
        self.title = title
        self.artist = artist
        self.album = album
        self.track_length = track_length
        self.sample_rate = sample_rate

    def __repr__(self):
        """返回歌曲信息的字符串表示"""
        return (f"Song(id={self.id}, title={self.title}, artist={self.artist}, "
                f"album={self.album}, length={self.track_length:.2f}s, "
                f"sample_rate={self.sample_rate}Hz, path={self.path})")

class WaitList:
    """等待播放的歌单"""
    def __init__(self):
        self.wait_list = []

    def add(self, Song):
        self.wait_list.append(Song)
        return self.wait_list
    
    def add_by_sid(self, sid):
        pass

    def move(self, wid, offset):
        wid = wid - 1
        offset = -offset    
        if 0 <= wid < len(self.wait_list):
            song = self.wait_list.pop(wid)
            new_pos = max(0, min(len(self.wait_list), wid + offset))
            self.wait_list.insert(new_pos, song)
        return self.wait_list

    def delete(self, wid):
        wid = wid - 1
        if 0 <= wid < len(self.wait_list):
            self.wait_list.pop(wid)
        return self.wait_list
    def move_first(self, wid):
        self.move(wid, wid)

    def get_list(self):
        return self.wait_list
    def get_idlist(self):
        num_list = [Song.id for Song in self.wait_list]
        return num_list
    def store(self, db_path):
        os.remove(db_path)
        """将等待列表保存到SQLite数据库"""
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))  # 确保目录存在

        # 创建数据库连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wait_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 歌曲ID
                sid INTEGER NOT NULL,                  -- 歌曲ID
                path TEXT NOT NULL,                    -- 文件路径
                title TEXT NOT NULL,                   -- 歌曲标题
                artist TEXT,                           -- 歌手
                album TEXT,                            -- 专辑
                track_length REAL,                     -- 歌曲时长
                sample_rate INTEGER                    -- 采样率
            )
        """)

        # 清空现有数据
        cursor.execute("DELETE FROM wait_list")

        # 插入新数据
        for song in self.wait_list:
            cursor.execute("""
                INSERT INTO wait_list (sid, path, title, artist, album, track_length, sample_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (song.id, song.path, song.title, song.artist, song.album, song.track_length, song.sample_rate))

        # 提交并关闭连接
        conn.commit()
        conn.close()

    def load(self, db_path):
        """从SQLite数据库加载等待列表"""
        # 确保数据库文件存在
        if not os.path.exists(db_path):
            print("数据库文件不存在")
            return

        # 创建数据库连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取数据并保持原来的顺序
        cursor.execute("SELECT sid, path, title, artist, album, track_length, sample_rate FROM wait_list ORDER BY id")
        rows = cursor.fetchall()

        # 更新wait_list为从数据库中加载的内容
        self.wait_list = [Song(*row) for row in rows]

        # 关闭连接
        conn.close()
    def store_backup(self):
        self.store(WAIT_LIST_DB_PATH)
    
    def load_backup(self):
        self.load(WAIT_LIST_DB_PATH)


    
if __name__ == "__main__":
    # wait_list = WaitList()
    # wait_list.add(1)
    # wait_list.add(2)
    # wait_list.add(3)
    # wait_list.add(4)
    # wait_list.add(5)
    # wait_list.add(6)
    # wait_list.add(7)
    # wait_list.add(4)
    # print(wait_list.get_list())
    # wait_list.move(2, 1)
    # print(wait_list.get_list())
    # wait_list.delete(3)
    # print(wait_list.get_list())
    # wait_list.move(3,6)
    # print(wait_list.get_list())
    # wait_list.move(3,-10)
    # print(wait_list.get_list())
    # wait_list.move_first(6)
    # print(wait_list.get_list())
    pass
