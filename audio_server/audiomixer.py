import numpy as np
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)


class AudioMixer:
    def __init__(self,
                 sample_rate=48000,
                 channels=2,
                 chunk_size=1920,
                 reverb_file_path="audio_server/reverb/naive.npy",
                 reverb_interval=10):

        # 初始化音频混合器
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size

        # 加载混响 IR
        self.reverb_IR = np.load(reverb_file_path)
        self.reverb_times = len(self.reverb_IR)
        self.reverb_interval = reverb_interval
        self.reverb_queue = deque(maxlen=self.reverb_times*reverb_interval)

        # 初始化reverse_queue
        for i in range(self.reverb_times * reverb_interval):
            self.reverb_queue.append(
                np.zeros((1, chunk_size), dtype=np.float32))

    def mix_frames(self,
                   audio_data_list: list[np.ndarray],
                   if_reverb: bool = False) -> np.ndarray:
        """
        异步混合音频帧
        """
        track_num = len(audio_data_list)
        mixed_audio = None

        for i in range(track_num):
            if audio_data_list[i].dtype == np.int16:
                audio_data_list[i] = audio_data_list[i].astype(np.float32) / 32768.0

        # 检查音频帧数量
        if track_num == 0:
            return None
        elif track_num == 1:
            mixed_audio = audio_data_list[0]
        elif track_num > 1:
            mixed_audio = np.mean(audio_data_list, axis=0)

        # 混响处理
        if if_reverb and mixed_audio is not None:
            mixed_audio = self.reverb(mixed_audio)

        return mixed_audio

    def reverb(self, audio_data: np.ndarray) -> np.ndarray:
        """
        对音频数据进行混响处理
        """
        self.reverb_queue.append(audio_data)

        # 从队列中取出音频数据并求和
        reverb_data = np.zeros_like(audio_data)

        for i in range(self.reverb_times):
            reverb_data += self.reverb_IR[i] * \
                self.reverb_queue[i*self.reverb_interval]

        return reverb_data
