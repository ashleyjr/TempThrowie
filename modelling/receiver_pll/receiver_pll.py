import sys
import numpy as np
import matplotlib.pyplot as plt

class DiscreteSim:

    def __init__(   self,
                    timestep_s = 1e-4):
        self.__time_s = 0
        self.timestep_s = timestep_s

    def tick(self):
        self.__time_s += self.timestep_s

class SquareWave(DiscreteSim):

    def __init__(   self,
                    timestep_s  = 1e-4,
                    freq_hz     = 1e3,
                    sim_s       = 6e-3,
                    phase_deg   = 0):
        DiscreteSim.__init__(self, timestep_s)
        self.__freq_hz    = freq_hz
        self.__period_s   = 1 / freq_hz
        self.__sim_s      = sim_s
        self.__phase_deg  = phase_deg
        self.__time_s     = 0
        self.__cycle      = self.__period_s * (phase_deg/360)

    def getOutput(self):
        return 1 if self.__cycle > (self.__period_s/2) else 0

    def tick(self):
        DiscreteSim.tick(self)
        self.__cycle  += self.timestep_s
        self.__cycle  %= self.__period_s

class Pll(SquareWave):

    def __init__(   self,
                    timestep_s  = 1e-4,
                    freq_hz     = 1e3,
                    sim_s       = 6e-3,
                    phase_deg   = 0):

        SquareWave.__init__(self, timestep_s, freq_hz, sim_s, phase_deg)
        self.i = 0

    def setInput(self, i):
        self.i = i

    def getOutput(self):
        return self.last

    def tick(self):
        SquareWave.tick(self)
        self.last = self.i

class Scope(DiscreteSim):

    def __init__(   self,
                    timestep_s = 1e-4,
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
        plt.xlabel("Time (s)")
        plt.savefig(filename)

    def tick(self):
        DiscreteSim.tick(self)
        for c in range(self.__channels):
            self.__samples[c].append(self.__sample[c])

def main(argv):
    wave = SquareWave(timestep_s=1e-6)
    scope = Scope(timestep_s=1e-6,channels=2)

    for i in range(10000):
        scope.measure(wave.getOutput(),0)
        scope.measure(wave.getOutput(),1)
        scope.tick()
        wave.tick()
    scope.saveScreen("graph.png")

if "__main__" == __name__:
    main(sys.argv)

