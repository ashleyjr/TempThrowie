import matplotlib.pyplot as plt
import scipy.fftpack
import numpy as np
import math
from scipy import signal

def fft(data):
    N = len(data)
    # sample spacing
    T = 1e-4
    x = np.linspace(0.0, N*T, N)
    y = data
    yf = scipy.fftpack.fft(y)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    yf = 2.0/N * np.abs(yf[:N//2])
    return xf, yf

# Read data
with open("filter.log", "r") as f:
    s = f.read()
    f.close()

# Create int array
raw = []
for c in s:
    if c == '0':
        raw.append(0)
    else:
        raw.append(1)

# Run the filter
y_1 = 0
timestep_s = 1e-4

lpf_f = 1010
lpf_rc = 1 / (2 * math.pi * lpf_f)
lpf_alpha = timestep_s / (lpf_rc + timestep_s)
lpf_beta = 1 - lpf_alpha

hpf_f = 990
hpf_rc = 1 / (2 * math.pi * hpf_f)
hpf_alpha = timestep_s / (hpf_rc + timestep_s)


# LPF
l=[]
for r in raw:
    y_0 = lpf_alpha * r
    y_0 += lpf_beta * y_1
    y_1 = y_0
    l.append(y_0)

# HPF
y_1 = 0
x_1 = 0
h=[]
for r in raw:
    y_0 = hpf_alpha * y_1
    y_0 += hpf_alpha * (r - x_1)
    y_1 = y_0
    x_1 = r
    h.append(y_0)

# BPF
y_1 = 0
b=[]
for r in l:
    y_0 = hpf_alpha * y_1
    y_0 += hpf_alpha * (r - x_1)
    y_1 = y_0
    x_1 = r
    b.append(y_0)


sos = signal.butter(3, [990,1010], 'bp', fs=10000, output='sos')
filtered = signal.sosfilt(sos, raw)

plt.subplot(10,1,1)
plt.plot(raw)

plt.subplot(10,1,2)
x,y=fft(raw)
plt.plot(x,y)
plt.ylim([0,0.05])

plt.subplot(10,1,3)
plt.plot(l)

plt.subplot(10,1,4)
x,y=fft(l)
plt.plot(x,y)
plt.ylim([0,0.05])

plt.subplot(10,1,5)
plt.plot(h)

plt.subplot(10,1,6)
x,y=fft(h)
plt.plot(x,y)
plt.ylim([0,0.05])

plt.subplot(10,1,7)
plt.plot(b)

plt.subplot(10,1,8)
x,y=fft(b)
plt.plot(x,y)
plt.ylim([0,0.05])

plt.subplot(10,1,9)
plt.plot(filtered)

plt.subplot(10,1,10)
x,y=fft(filtered)
plt.plot(x,y)
plt.ylim([0,0.05])


plt.show()
