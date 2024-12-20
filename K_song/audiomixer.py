import numpy as np
import asyncio


class AudioMixer:
    def __init__(self,
                 sample_rate=48000,
                 channels=2):
        # 初始化音频混合器
        self.sample_rate = sample_rate
        self.channels = channels

    async def mix_frames(self, audio_data_list: list[np.ndarray]) -> np.ndarray:
        """
        异步混合音频帧
        """
        track_num = len(audio_data_list)

        # 检查音频帧数量
        if track_num == 1:
            return audio_data_list[0]
        if track_num == 0:
            return None

        # 将所有音频帧求和取平均，假定所有音频帧的长度是一致的
        mixed_audio = await asyncio.to_thread(
            np.sum, audio_data_list, axis=0
        )

        return mixed_audio
