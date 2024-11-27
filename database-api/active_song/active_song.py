import time

class ActiveSong:
    """当前播放的歌曲"""
    def __init__(self, song_data=None):
        self.sid = None
        self.song_data = song_data
        self.pause = True
        self.time = 0.0
        self.time_stamp = None
        self.volume = 50  # 默认音量
        if self.song_data and hasattr(self.song_data, 'id'):
            self.sid = self.song_data.id
        
        
    def play(self, sid):
        self.sid = sid
        self.pause = False
        self.time_stamp = time.time()

    def pause_song(self):
        self.pause = True
        self.time += time.time() - self.time_stamp if self.time_stamp else 0
        self.time_stamp = None

    def adjust_vol(self, volume):
        self.volume = max(0, min(100, volume))  # 限制音量范围为 0~100

    def adjust_time(self, time_position):
        self.time = time_position
        self.time_stamp = time.time()



    