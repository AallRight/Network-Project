import asyncio
import numpy as np
import logging
import pyaudio


class AudioRecorder:
    def __init__(self,
                 format=pyaudio.paInt16,
                 sample_rate=48000,
                 frames_per_buffer=256,
                 chunk_size=1920,
                 channels=2):
        self.format = format
        self.sample_rate = sample_rate
        self.frames_per_buffer = frames_per_buffer
        self.chunk_size = chunk_size
        self.channels = channels

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=format,
                                  channels=channels,
                                  rate=sample_rate,
                                  frames_per_buffer=frames_per_buffer,
                                  input=True)

    async def record_frame(self) -> np.ndarray:
        # 从麦克风读取音频帧
        audio_data = self.stream.read(self.chunk_size//self.channels)
        audio_data = np.frombuffer(audio_data, dtype=np.int16).reshape(1, -1)

        return audio_data

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


if __name__ == '__main__':
    async def main():
        recorder = AudioRecorder()
        while True:
            await recorder.record_frame()
        recorder.close()

    asyncio.run(main())
