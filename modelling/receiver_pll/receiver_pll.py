import sys
import math
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
                    timestep_s  = 1e-6):
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
        self.phase = self.dn - self.up


class Lf(DiscreteSim):
    def __init__(   self,
                    timestep_s  = 1e-6,
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
        self.y_1  = self.y_0
        self.y_0  = self.alpha * self.x
        self.y_0 += self.beta * self.y_1


class Integrator(DiscreteSim):
    def __init__(   self,
                    timestep_s  = 1e-6):
        DiscreteSim.__init__(self, timestep_s)
        self.x = 0
        self.x_0 = 0
        self.x_1 = 0
        self.integral = 0

    def setInput(self, x):
        self.x = x

    def getOutput(self):
        return self.integral

    def tick(self):
        DiscreteSim.tick(self)
        self.x_1 = self.x_0
        self.x_0 = self.x
        self.integral += ((self.x_0 + self.x_1) / 2)


class Pid(DiscreteSim):
    def __init__(   self,
                    timestep_s  = 1e-6,
                    p           = 2e-3,
                    i           = 1e-7):
        DiscreteSim.__init__(self, timestep_s)
        self.p = p
        self.i = i
        self.x = 0
        self.y = 0
        self.integral = 0

    def setInput(self, x):
        self.x_0 = x

    def getOutput(self):
        return self.y

    def tick(self):
        DiscreteSim.tick(self)
        self.x_1 = self.x_0
        self.integral += ((self.x_0 + self.x_1) / 2)
        self.y  = self.x_0 * self.p
        self.y += self.integral * self.i


class Vco(DiscreteSim):
    def __init__(   self,
                    timestep_s  = 1e-6,
                    min_freq_hz = 1500,
                    max_freq_hz = 2500):
        DiscreteSim.__init__(self, timestep_s)
        self.__max_period_s = 1 / float(min_freq_hz)
        self.__min_period_s = 1 / float(max_freq_hz)
        self.period_s = 1e-2
        self.cycle  = 0

    def control(self, c):
        self.period_s = c
        if self.period_s > self.__max_period_s:
            self.period_s = self.__max_period_s
        if self.period_s < self.__min_period_s:
            self.period_s = self.__min_period_s

    def getPeriodS(self):
        return self.period_s

    def getOutput(self):
        return 1 if self.cycle > (self.period_s/2) else 0

    def tick(self):
        DiscreteSim.tick(self)
        self.cycle += self.timestep_s
        if self.cycle >= self.period_s:
            self.cycle = 0

class Div2(DiscreteSim):
    def __init__(   self,
                    timestep_s  = 1e-6):
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
                    timestep_s = 1e-6,
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
        t = 1e3*np.arange(0, sim_s, self.timestep_s)
        plt.rcParams.update({'font.size': 5})
        for c in range(self.__channels):
            plt.subplot(self.__channels, 1, c+1)
            plt.plot(t, self.__samples[c])
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
    wave = SquareWave(phase_deg=66)
    vco = Vco()
    pd = PhaseDet()
    igr = Integrator()
    pid = Pid()
    lf = Lf()
    div = Div2()
    scope = Scope(channels=6)
    for i in range(50000):
        pd.setRef(wave.getOutput())
        pd.setVco(div.getOutput())
        igr.setInput(pd.getOutput())
        lf.setInput(pd.getOutput())
        pid.setInput(lf.getOutput())
        vco.control(pid.getOutput())
        div.setInput(vco.getOutput())
        scope.measure(wave.getOutput(),0)
        scope.measure(pd.getOutput(),1)
        scope.measure(lf.getOutput(),2)
        scope.measure(pid.getOutput(),3)
        scope.measure(vco.getOutput(),4)
        scope.measure(vco.getPeriodS(),5)
        igr.tick()
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

