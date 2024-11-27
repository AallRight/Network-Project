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
        
        
    def play(self, sid, time_stamp):
        self.sid = sid
        self.pause = False
        self.time_stamp = time_stamp
    
    def play_song(self, sid, time_stamp, song_data):
        self.sid = sid
        self.song_data = song_data
        self.pause = False
        self.time_stamp = time_stamp

    def pause_song(self, time):
        self.pause = True
        self.time = time

    def adjust_vol(self, volume):
        self.volume = max(0, min(100, volume))  # 限制音量范围为 0~100
        return self.volume

    def adjust_time(self, time_position):
        self.time = time_position
        self.time_stamp = time.time()



    