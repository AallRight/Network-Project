import os
import sqlite3
from data.song import Song
from typing import *

class Waitlist:
    def __init__(self, db_path: str, db: bool = False):
        self.waitlist: list[Song] = []
        self.db_path = db_path
        self.db = db
        if self.db:
            self.__initialize_database()
            self.__load()
    
    def __del__(self):
        if self.db:
            self.__store()

    def add(self, song: Song):
        self.waitlist.append(song)

    def move(self, wid: int, offset: int):
        wid -= 1
        if 0 <= wid < len(self.waitlist):
            song = self.waitlist.pop(wid)
            new_pos = max(0, min(len(self.waitlist), wid + offset))
            self.waitlist.insert(new_pos, song)

    def delete(self, wid: int):
        wid -= 1
        if 0 <= wid < len(self.waitlist):
            self.waitlist.pop(wid)

    def get_length(self):
        return len(self.waitlist)
    
    def get_song(self, wid: int) -> Optional[Song]:
        wid -= 1
        if 0 <= wid < len(self.waitlist):
            return self.waitlist[wid]
        return None

    def get_song_list(self) -> List[Song]:
        return self.waitlist
    
    def get_sid_list(self) -> List[int]:
        return [song.sid for song in self.waitlist]
    
    def __initialize_database(self):
        if not os.path.exists(self.db_path):
            print(f"Create a new database in '{self.db_path}'.")

        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wait_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sid INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    title TEXT NOT NULL,
                    artist TEXT,
                    album TEXT,
                    track_length REAL,
                    sample_rate INTEGER
                )
            """)
            conn.commit()
        
    def __store(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM wait_list")
            
            for song in self.waitlist:
                cursor.execute("""
                    INSERT INTO wait_list (sid, path, title, artist, album, track_length, sample_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (song.sid, song.path, song.title, song.artist, song.album, song.track_length, song.sample_rate))

            conn.commit()


    def __load(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sid, path, title, artist, album, track_length, sample_rate FROM wait_list ORDER BY id")
            rows = cursor.fetchall()
            self.waitlist = [Song(*row) for row in rows]
            conn.commit()
        
    def __str__(self):
        return f"{self.waitlist}, database {self.db_path}"