import numpy as np
from av.audio.frame import AudioFrame
import asyncio
from concurrent.futures import ThreadPoolExecutor


class AudioMixer:
    def __init__(self, sample_rate=48000, channels=2):
        # 初始化音频混合器
        self.sample_rate = sample_rate
        self.channels = channels
        self.executor = ThreadPoolExecutor()  # 线程池执行器

    async def mix_frames(self, frames: list[AudioFrame]):
        """
        异步混合音频帧
        """
        track_num = len(frames)

        # 检查音频帧数量
        if track_num == 1:
            return frames[0]

        # 使用线程池异步混音
        loop = asyncio.get_event_loop()
        mixed_frame = await loop.run_in_executor(
            self.executor, self._mix_frames_sync, frames
        )

        return mixed_frame

    def _mix_frames_sync(self, frames: list[AudioFrame]):
        """
        同步混音方法，用于在线程池中运行
        """
        track_num = len(frames)

        # 初始化混合结果
        mixed_frame = frames[0].to_ndarray()

        # 线性叠加
        for idx in range(1, track_num):
            mixed_frame += frames[idx].to_ndarray()

        # 平均化混音结果
        mixed_frame //= track_num

        # 创建新的音频帧
        return AudioFrame.from_ndarray(mixed_frame, format="s16p")
