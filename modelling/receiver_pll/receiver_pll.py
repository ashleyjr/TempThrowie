import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import ctypes
import os

TIMESTEP_S = 1e-5
SIM_TIME_S = 1e-2

class DiscreteSim:

    def __init__(   self,
                    timestep_s = TIMESTEP_S):
        self.__time_s = 0
        self.timestep_s = timestep_s

    def tick(self):
        self.__time_s += self.timestep_s

    def getTime(self):
        return self.__time_s

class SquareWave(DiscreteSim):

    def __init__(   self,
                    timestep_s  = TIMESTEP_S,
                    freq_hz     = 1e3,
                    phase_deg   = 45):
        DiscreteSim.__init__(self, timestep_s)

        self.__freq_hz    = freq_hz
        self.period_s     = 1 / freq_hz
        self.cycle        = (self.period_s * float(phase_deg))/float(360)

    def getOutput(self):
        return 1 if self.cycle > (self.period_s/2) else 0

    def tick(self):
        DiscreteSim.tick(self)
        self.cycle += self.timestep_s
        if self.cycle >= self.period_s:
            self.cycle = 0

class PhaseDet(DiscreteSim):
    def __init__(   self,
                    timestep_s  = TIMESTEP_S):
        DiscreteSim.__init__(self, timestep_s)
        self.ref_0 = 0
        self.ref_1 = 0
        self.vco_0 = 0
        self.vco_1 = 0
        self.up = 0
        self.dn = 0
        self.phase = 0

    def setRef(self, x):
        self.ref = x

    def setVco(self, x):
        self.vco = x

    def getOutput(self):
        return self.phase

    def tick(self):
        DiscreteSim.tick(self)
        self.ref_1 = self.ref_0
        self.vco_1 = self.vco_0
        self.ref_0 = self.ref
        self.vco_0 = self.vco
        ref_clk    = (self.ref_1 == 0) and (self.ref_0 == 1)
        vco_clk    = (self.vco_1 == 0) and (self.vco_0 == 1)
        self.up    = 1 if(ref_clk) else self.up
        self.dn    = 1 if(vco_clk) else self.dn
        reset      = self.up & self.dn
        self.up    = 0 if(reset) else self.up
        self.dn    = 0 if(reset) else self.dn
        self.phase = self.up - self.dn

class Lf(DiscreteSim):
    def __init__(   self,
                    timestep_s  = TIMESTEP_S,
                    f           = 20):
        DiscreteSim.__init__(self, timestep_s)
        self.x = 0
        self.y_0 = 0
        self.y_1 = 0
        rc = 1 / (2 * math.pi * f)
        self.alpha = self.timestep_s / (rc + self.timestep_s)
        self.beta = 1 - self.alpha

    def setInput(self, x):
        self.x = x

    def getOutput(self):
        return self.y_0

    def tick(self):
        DiscreteSim.tick(self)
        self.y_0  = self.alpha * self.x
        self.y_0 += self.beta * self.y_1
        self.y_1  = self.y_0

class Pid(DiscreteSim):
    def __init__(   self,
                    timestep_s  = TIMESTEP_S,
                    p           = 1600,
                    i           = 21):
        DiscreteSim.__init__(self, timestep_s)
        self.p = p
        self.i = i
        self.x = 0
        self.y = 0
        self.x_0 = 0
        self.x_1 = 0
        self.integral = 0

    def setInput(self, x):
        self.x_0 = x

    def getOutput(self):
        return self.y

    def tick(self):
        DiscreteSim.tick(self)
        self.integral += ((self.x_0 + self.x_1) / 2)
        self.y  = self.x_0 * self.p
        self.y += self.integral * self.i
        self.x_1 = self.x_0

class Vco(SquareWave):
    def __init__(   self,
                    timestep_s  = TIMESTEP_S,
                    min_freq_hz = 100,
                    max_freq_hz = 10000):
        SquareWave.__init__(self, timestep_s)
        self.__max_period_s = 1 / float(min_freq_hz)
        self.__min_period_s = 1 / float(max_freq_hz)
        self.period_s = self.__max_period_s
        self.cycle = 0

    def control(self, c):
        self.period_s = (1/(0.00001+c))
        if self.period_s > self.__max_period_s:
            self.period_s = self.__max_period_s
        if self.period_s < self.__min_period_s:
            self.period_s = self.__min_period_s

class Div2(DiscreteSim):
    def __init__(   self,
                    timestep_s  = TIMESTEP_S):
        DiscreteSim.__init__(self, timestep_s)
        self.x_0 = 0
        self.x_1 = 0
        self.y = 0

    def setInput(self, x):
        self.x = x

    def getOutput(self):
        return self.y

    def tick(self):
        DiscreteSim.tick(self)
        self.x_1 = self.x_0
        self.x_0 = self.x
        clk = (self.x_0 == 1) and (self.x_1 == 0)
        if(clk):
            self.y = 1 - self.y

class Scope(DiscreteSim):

    def __init__(   self,
                    timestep_s = TIMESTEP_S,
                    plotstep_s = 1e-3,
                    channels   = 1):
        DiscreteSim.__init__(self, timestep_s)
        self.plotstep_s = plotstep_s
        self.__channels = channels
        self.__samples = []
        for c in range(self.__channels):
            self.__samples.append([])
        self.__sample = [0] * self.__channels

    def measure(self, sample, channel):
        self.__sample[channel] = sample

    def saveScreen(self, filename):
        sim_s = len(self.__samples[0]) * self.timestep_s
        t = 1e3 * np.arange(0, sim_s, self.timestep_s)
        plt.rcParams.update({'font.size': 5})
        for c in range(self.__channels):
            plt.subplot(self.__channels, 1, c+1)
            plt.plot(t[0:len(self.__samples[c])], self.__samples[c])
            plt.xlim(0,t[-1])
            plt.xticks([])
        plt.xticks(np.arange(0, sim_s*1e3, self.plotstep_s*1e3), rotation=45)
        plt.xlabel("Time (ms)")
        plt.xticks
        plt.savefig(filename, dpi=150)

    def tick(self):
        DiscreteSim.tick(self)
        for c in range(self.__channels):
            self.__samples[c].append(self.__sample[c])

def main(argv):

    # Load C implementation
    dir_path = os.path.dirname(os.path.realpath(__file__))
    so = os.path.join(dir_path, "receiver_pll.so")
    impl = ctypes.CDLL(so)
    impl.receiver_pll_init()

    wave    = SquareWave(phase_deg=66)
    vco     = Vco()
    pd      = PhaseDet()
    pid     = Pid()
    lf      = Lf()
    div     = Div2()
    scope   = Scope(channels=7)
    error   = 0

    while wave.getTime() < SIM_TIME_S:
        pd.setRef(      wave.getOutput())
        pd.setVco(      vco.getOutput())
        lf.setInput(    pd.getOutput())
        pid.setInput(   lf.getOutput())
        vco.control(    pid.getOutput())
        div.setInput(   vco.getOutput())

        output = impl.receiver_pll(wave.getOutput())
        error += abs(output - vco.getOutput())

        scope.measure(wave.getOutput(),     0)
        scope.measure(pd.getOutput(),       1)
        scope.measure(lf.getOutput(),       2)
        scope.measure(pid.getOutput(),      3)
        scope.measure(vco.getOutput(),      4)

        scope.measure(output,   5)
        scope.measure(error,    6)

        lf.tick()
        div.tick()
        pd.tick()
        scope.tick()
        wave.tick()
        pid.tick()
        vco.tick()

    scope.saveScreen("graph.png")

if "__main__" == __name__:
    main(sys.argv)

