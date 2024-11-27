class Mlibrary:
    """歌曲库"""
    def __init__(self):
        self.songs = {}

    def add_song(self, sid, path, title, artist, album, track_length, sample_rate):
        self.songs[sid] = {
            "path": path,
            "title": title,
            "artist": artist,
            "album": album,
            "track_length": track_length,
            "sample_rate": sample_rate,
        }

    def get_song(self, sid):
        return self.songs.get(sid)

if __name__ == "__main__":
    m = Mlibrary()
    m.add_song(1, "path/to/song", "Song Title", "Artist", "Album", 180, 44100)
    print(m.get_song(1))
    print(m.get_song(2))

