import os
import sqlite3
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from data.song import Song
from typing import *
from functools import lru_cache

class MLibrary:
    def __init__(self, db_path: str, music_path: str):
        self.db_path = db_path
        self.music_path = music_path
        self.__clear_database()
        self.__initialize_database()
        self.__append_songs_in_directory(music_path)

    def __initialize_database(self):
        if not os.path.exists(self.db_path):
            print(f"Create a new database in '{self.db_path}'.")

        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                title TEXT NOT NULL,
                artist TEXT,
                album TEXT,
                track_length REAL,
                sample_rate INTEGER
            )
            """)
            conn.commit()

    def __clear_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS songs")
            conn.commit()

    def __append_song(self, path, title, artist, album, track_length, sample_rate):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO songs (path, title, artist, album, track_length, sample_rate)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (path, title, artist, album, track_length, sample_rate))

            conn.commit()
    
    def __append_songs_in_directory(self, directory: str):
        sid = 1
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith((".mp3", ".oga", ".ogg", ".flac")):
                    file_path = os.path.join(root, file)

                    try:
                        if file.endswith(".mp3"):
                            audio = MP3(file_path, ID3=EasyID3)
                        elif file.endswith((".oga", ".ogg")):
                            audio = OggVorbis(file_path)
                        elif file.endswith(".flac"):
                            audio = FLAC(file_path)

                        track_length = audio.info.length
                        sample_rate = audio.info.sample_rate
                        title = audio.get("title", ["Unknown"])[0]
                        artist = audio.get("artist", ["Unknown"])[0]
                        album = audio.get("album", ["Unknown"])[0]

                        self.__append_song(file_path, title, artist, album, track_length, sample_rate)
                        sid += 1
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        continue

    @lru_cache(maxsize=128)
    def get_songs_by_keyword(self, keyword: str) -> List[Song]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
            SELECT id, path, title, artist, album, track_length, sample_rate 
            FROM songs
            WHERE title LIKE ? OR artist LIKE ?
            """
            cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            rows = cursor.fetchall()
            songs = [Song(*row) for row in rows]
            return songs
        
    
    def get_songs_by_ids(self, sids: List[int])-> List[Optional[Song]]:
        if not sids:
            return []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            placeholders = ', '.join(['?'] * len(sids))
            query = f"SELECT * FROM songs WHERE id IN ({placeholders})"
            cursor.execute(query, sids)

            results = cursor.fetchall()
            result_dict = {row[0]: row for row in results}
            songs = []
            for sid in sids:
                if sid in result_dict:
                    songs.append(Song(*result_dict[sid]))
                else:
                    songs.append(None)

            return songs
        
    
    def get_num_songs(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM songs")
            count = cursor.fetchone()[0]
            return count