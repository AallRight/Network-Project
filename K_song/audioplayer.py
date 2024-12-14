import pyaudio
import numpy as np
from pydub import AudioSegment
import asyncio


class AudioPlayer:
    def __init__(self,
                 format=pyaudio.paInt16,
                 sample_rate=48000,
                 frames_per_buffer=256,
                 channels=2):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=format,
                                  channels=channels,
                                  rate=sample_rate,
                                  frames_per_buffer=frames_per_buffer,
                                  output=True)

    async def play_frame(self, audio_data: np.ndarray):
        # 将 AudioFrame 转换为字节对象
        self.stream.write(audio_data.tobytes())

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


async def main():
    audio_path = "music/时暮的思眷.wav"
    audio = AudioSegment.from_file(audio_path)
    player = AudioPlayer()

    # 将音频数据分块播放
    chunk_size = 1024
    for i in range(0, len(audio.raw_data), chunk_size):
        chunk = audio.raw_data[i:i + chunk_size]
        audio_data = np.frombuffer(
            chunk, dtype=np.int16).reshape(-1, 2)  # 转为双声道格式
        audio_data = audio_data.mean(axis=1).astype(np.int16)
        # 将 chunk 转换为 AudioFrame
        await player.play_frame(audio_data)

    player.close()

if __name__ == '__main__':
    asyncio.run(main())
