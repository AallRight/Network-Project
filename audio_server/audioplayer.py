import pyaudio
import numpy as np
from pydub import AudioSegment
import asyncio


class AudioPlayer:
    def __init__(self,
                 format=pyaudio.paInt16,
                 sample_rate=48000,
                 frames_per_buffer=1920,
                 channels=2):
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=format,
                                  channels=channels,
                                  rate=sample_rate,
                                  frames_per_buffer=frames_per_buffer,
                                  output=True)

        # ?debug: 初始化WAV文件写入器
        # self.wav_writer = wave.open("output.wav", "wb")
        # self.wav_writer.setnchannels(channels)
        # self.wav_writer.setsampwidth(self.p.get_sample_size(format))
        # self.wav_writer.setframerate(sample_rate)

    def play_frame(self, audio_data: np.ndarray):
        # 将 AudioFrame 转换为字节对象
        if audio_data.dtype != np.int16:
            audio_data = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
        self.stream.write(audio_data.tobytes())
        # ?debug: 写入WAV文件
        # self.wav_writer.writeframes(audio_data.tobytes())

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


async def main():
    audio_path = "music/时暮的思眷.wav"
    audio = AudioSegment.from_file(audio_path)
    player = AudioPlayer()

    # 将音频数据分块播放
    chunk_size = 480000
    for i in range(0, len(audio.raw_data), chunk_size):
        chunk = audio.raw_data[i:i + chunk_size]
        audio_data = np.frombuffer(
            chunk, dtype=np.int16)
        # 将 chunk 转换为 AudioFrame
        await player.play_frame(audio_data)
        print(f"播放进度：{i / len(audio.raw_data) * 100:.2f}%")

    player.close()

if __name__ == '__main__':
    asyncio.run(main())
