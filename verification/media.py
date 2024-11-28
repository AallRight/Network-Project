import pyaudio
import numpy as np
import queue
import threading

class Player:
    def __init__(self, channels=1, rate=44100):
        self.channels = channels
        self.rate = rate
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_playing = False
        self.buffer = queue.Queue(maxsize=5)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._play_thread)

    def start(self):
        if not self.is_playing:
            self.stream = self.p.open(format=pyaudio.paInt16,
                                       channels=self.channels,
                                       rate=self.rate,
                                       output=True)
            self.is_playing = True
            self.stop_event.clear()
            self.thread.start()

    def stop(self):
        if self.is_playing:
            self.stop_event.set()
            self.thread.join()
            self.stream.stop_stream()
            self.stream.close()
            self.is_playing = False

    def write(self, data):
        if self.is_playing:
            try:
                self.buffer.put(data, timeout=0.01)
            except queue.Full:
                pass

    def _play_thread(self):
        while not self.stop_event.is_set():
            try:
                data = self.buffer.get(timeout=0.01)
                self.stream.write(data)
            except queue.Empty:
                continue

    def __del__(self):
        self.stop()  # 确保停止播放
        self.p.terminate()