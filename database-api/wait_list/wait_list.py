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

    def move(self, wid, offset):
        wid = wid - 1
        offset = -offset    
        if 0 <= wid < len(self.wait_list):
            song = self.wait_list.pop(wid)
            new_pos = max(0, min(len(self.wait_list), wid + offset))
            self.wait_list.insert(new_pos, song)

    def delete(self, wid):
        wid = wid - 1
        if 0 <= wid < len(self.wait_list):
            self.wait_list.pop(wid)
    def move_first(self, wid):
        self.move(wid, wid)

    def get_list(self):
        return self.wait_list
    def get_idlist(self):
        num_list = [Song.id for Song in self.wait_list]
        return num_list
    def store(self):
        pass

    
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
