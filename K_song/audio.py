import pyaudio
import wave

# 打开音频文件
filename = 'test.wav'  # 替换为你的音频文件
wf = wave.open(filename, 'rb')

# 初始化 PyAudio
p = pyaudio.PyAudio()

# 打开音频流
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# 播放音频
data = wf.readframes(1024)
while data:
    stream.write(data)
    data = wf.readframes(1024)

# 关闭
stream.stop_stream()
stream.close()
p.terminate()
