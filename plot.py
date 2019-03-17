import matplotlib.pyplot as plt
import numpy as np

data = np.genfromtxt('frap.txt', dtype=np.float32)
data = data / data[0]
data = data[1:]

plt.figure()
plt.ylim(0, 1)
plt.scatter(range(0, 150, 5), data)
plt.xlabel('Time (s)', fontsize=14)
plt.ylabel('Fractional Recovery', fontsize=14)
plt.savefig('plot.png')
