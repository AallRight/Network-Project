import numpy as np

num = 4

# 创建一个 NumPy 数组
data = np.exp(-np.arange(num) * 0.75)
# 将数组归一化，使其求和为1
data /= np.sum(data)
data = np.flip(data)
print(data)

# 保存数组到 .npy 文件
np.save('K_song/reverb/naive.npy', data)
