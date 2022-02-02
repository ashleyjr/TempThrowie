from throwieConstants import throwieConstants as cnsts
import matplotlib.pyplot as plt
import numpy as np
import scipy.fftpack
from scipy import signal

class throwieTransmission:

    def __init__(self, data):
        self.data = data

        # Check the data
        assert len(self.data) == cnsts.RX_LEN
        for d in self.data:
            assert d in ['0','1']

        # Convert to ints
        self.data=[]
        for d in data:
            self.data.append(ord(d)-ord('0'))

    def fft(self, name=None):
        N = len(self.data)
        T = 1e-4
        x = np.linspace(0.0, N*T, N)
        yf = scipy.fftpack.fft(self.data)
        yf = 2.0/N * np.abs(yf[:N//2])
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        return xf, yf

    def filter(self):
        lpf = signal.butter(2, 1000, 'lp', fs=10000, output='sos')
        return signal.sosfilt(lpf, self.data)

    def getData(self):
        return self.data

    def getEdges(self):
        edges = []
        for i in range(len(self.data)-1):
            if self.data[i] ^ self.data[i+1]:
                edges.append(i)
        return edges

    def getDeltas(self):
        deltas = []
        edges = self.getEdges()
        for i in range(len(edges)-1):
            delta = edges[i+1] - edges[i]
            deltas.append(delta)
        return deltas

    def plot(self, name, x, y=None):
        if y == None:
            plt.plot(x)
        else:
            plt.plot(x,y)
        plt.savefig(name, dpi=200)
        plt.close()

    def hist(self, name, x):
        plt.hist(x)
        plt.savefig(name, dpi=200)
        plt.close()
