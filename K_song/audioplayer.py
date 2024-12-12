import pyaudio
import numpy as np
from pydub import AudioSegment
import asyncio
from av import AudioFrame


class AudioPlayer:
    def __init__(self, format=pyaudio.paInt16, sample_rate=48000, channels=2):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=format,
                                  channels=channels,
                                  rate=sample_rate,
                                  output=True)

    async def play_frame(self, frame: AudioFrame):
        # 将 AudioFrame 转换为字节对象
        audio_data = frame.to_ndarray().tobytes()
        self.stream.write(audio_data)

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
        audio_data = np.frombuffer(chunk, dtype=np.int16)
        audio_data = np.tile(audio_data, (2, 1))
        # 将 chunk 转换为 AudioFrame
        frame = AudioFrame.from_ndarray(
            audio_data, format="s16p")
        await player.play_frame(frame)
        # await asyncio.sleep(chunk_size / audio.frame_rate)

    player.close()

if __name__ == '__main__':
    asyncio.run(main())
