class WaitList:
    """等待播放的歌单"""
    def __init__(self):
        self.wait_list = []

    def add(self, sid):
        self.wait_list.append(sid)

    def move(self, wid, offset):
        if 0 <= wid < len(self.wait_list):
            song = self.wait_list.pop(wid)
            new_pos = max(0, min(len(self.wait_list), wid + offset))
            self.wait_list.insert(new_pos, song)

    def delete(self, wid):
        if 0 <= wid < len(self.wait_list):
            self.wait_list.pop(wid)

    def get_list(self):
        return self.wait_list
