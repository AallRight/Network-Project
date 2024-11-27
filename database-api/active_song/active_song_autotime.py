import time
# import sys
# import os 
# parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    
# sys.path.append(parent_dir)
# wait_list_dir = parent_dir + "\wait_list"
# sys.path.append(wait_list_dir)
# from wait_list.wait_list import Song

class ActiveSong:
    """当前播放的歌曲"""
    def __init__(self, song_data=None):
        self.sid = None
        self.song_data = song_data
        self.pause = True
        self.time = 0.0  # 已播放的时长
        self.time_stamp = None  # 当前时间戳，用于计算播放时长
        self.volume = 50  # 默认音量
        
        # 如果 song_data 不是 None 且有 id 属性，则将 self.sid 设置为 song_data.id
        if self.song_data and hasattr(self.song_data, 'id'):
            self.sid = self.song_data.id
    
    def play(self, sid):
        """开始播放歌曲"""
        self.sid = sid
        self.pause = False
        self.time_stamp = time.time()  # 记录播放的起始时间
    
    def pause_song(self):
        """暂停歌曲播放"""
        if not self.pause and self.time_stamp:
            # 更新已播放的时长
            self.time += time.time() - self.time_stamp
        self.pause = True
        self.time_stamp = None  # 清空时间戳
    
    def adjust_vol(self, volume):
        """调整音量"""
        self.volume = max(0, min(100, volume))  # 限制音量范围为 0~100
    
    def adjust_time(self, time_position):
        """调整歌曲的播放位置"""
        self.time = time_position
        self.time_stamp = time.time()
    
    def get_played_time(self):
        """获取当前已播放的时长"""
        if not self.pause and self.time_stamp:
            # 如果正在播放，则计算当前时间到开始时间的差值
            return self.time + (time.time() - self.time_stamp)
        return self.time

# 示例使用：
if __name__ == "__main__":
    active_song = ActiveSong(song_data=None)  # 假设有个song_data传入
    active_song.play(1)  # 假设开始播放歌曲
    time.sleep(2)  # 模拟歌曲播放2秒
    print(f"播放时长: {active_song.get_played_time()}秒")
    active_song.pause_song()  # 暂停播放
    time.sleep(1)  # 暂停1秒
    print(f"已播放时长（暂停后）：{active_song.get_played_time()}秒")
    active_song.play(1)  # 恢复播放
    time.sleep(1)  # 再播放1秒
    print(f"恢复播放后的时长: {active_song.get_played_time()}秒")
