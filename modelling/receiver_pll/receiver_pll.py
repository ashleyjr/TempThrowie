import sys
import numpy as np
import matplotlib.pyplot as plt

class DiscreteSim:

    def __init__(   self,
                    timestep_s = 1e-6):
        self.__time_s = 0
        self.timestep_s = timestep_s

    def tick(self):
        self.__time_s += self.timestep_s

class SquareWave(DiscreteSim):

    def __init__(   self,
                    timestep_s  = 1e-6,
                    freq_hz     = 1e3,
                    phase_deg   = 0):
        DiscreteSim.__init__(self, timestep_s)

        self.__freq_hz    = freq_hz
        self.period_s     = 1 / freq_hz
        self.__phase_deg  = phase_deg
        self.cycle        = self.period_s * (phase_deg/360)

    def getOutput(self):
        return 1 if self.cycle > (self.period_s/2) else 0

    def tick(self):
        DiscreteSim.tick(self)
        self.cycle  += self.timestep_s
        self.cycle  %= self.period_s

class PhaseDet(DiscreteSim):
    def __init__(   self,
                    timestep_s  = 1e-6):
        DiscreteSim.__init__(self, timestep_s)
        self.a = 0
        self.b = 0

    def setInputA(self, a):
        self.a = a

    def setInputB(self, b):
        self.b = b

    def getOutput(self):
        return self.a - self.b

class Vco(SquareWave):
    def __init__(   self,
                    timestep_s  = 1e-6,
                    min_freq_hz = 2e3,
                    max_freq_hz = 1e6):
        SquareWave.__init__(self, timestep_s)
        self.__max_period_s = 1 / float(min_freq_hz)
        self.__min_period_s = 1 / float(max_freq_hz)
        self.period_s = self.__max_period_s
        self.cycle  = 0

    def control(self, c):
        self.period_s += c
        if self.period_s > self.__max_period_s:
            self.period_s = self.__max_period_s
        if self.period_s < self.__max_period_s:
            self.period_s = self.__min_period_s

class Scope(DiscreteSim):

    def __init__(   self,
                    timestep_s = 1e-6,
                    channels   = 1):
        DiscreteSim.__init__(self, timestep_s)
        self.__channels = channels
        self.__samples = []
        for c in range(self.__channels):
            self.__samples.append([])
        self.__sample = [0] * self.__channels

    def measure(self, sample, channel):
        self.__sample[channel] = sample

    def saveScreen(self, filename):
        sim_s = len(self.__samples[0]) * self.timestep_s
        t = np.arange(0, sim_s, self.timestep_s)
        for c in range(self.__channels):
            plt.subplot(self.__channels, 1, c+1)
            plt.plot(t, self.__samples[c])
            plt.xlim(0,t[-1])
        plt.xlabel("Time (s)")
        plt.savefig(filename, dpi=150)

    def tick(self):
        DiscreteSim.tick(self)
        for c in range(self.__channels):
            self.__samples[c].append(self.__sample[c])

def main(argv):
    wave = SquareWave()
    vco = Vco()
    pd = PhaseDet()
    scope = Scope(channels=3)
    for i in range(10000):
        pd.setInputA(wave.getOutput())
        pd.setInputB(vco.getOutput())
        scope.measure(wave.getOutput(),0)
        scope.measure(vco.getOutput(),1)
        scope.measure(pd.getOutput(),2)
        pd.tick()
        scope.tick()
        wave.tick()
        vco.tick()
    scope.saveScreen("graph.png")

if "__main__" == __name__:
    main(sys.argv)

