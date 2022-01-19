from throwieConstants import throwieConstants as cnsts
import matplotlib.pyplot as plt

class throwieTransmission():

    def __init__(self, data):
        self.data = data

        self.len = 4000
        # Check the data
        assert len(self.data) == cnsts.RX_LEN
        for d in self.data:
            assert d in ['0','1']

        # Convert to ints
        self.data=[]
        for d in data:
            self.data.append(ord(d)-ord('0'))

    def createWave(self, phase):
        wave=[]
        period = phase
        for i in range(cnsts.RX_LEN-1):
            if period >= 5:
                wave.append(1)
            else:
                wave.append(0)
            period+=1
            period%=10
        return wave

    def cmpWaves(self, a, b):
        d = 0
        for i in range(cnsts.RX_LEN-1):
            d += abs(a[i] - b[i])
        return d

    def findSamplePhase(self):
        w = self.createWave(0)
        test = self.cmpWaves(self.data, w)
        best = 0
        mini = test
        for i in range(1,10):
            w = self.createWave(i)
            test = self.cmpWaves(self.data, w)
            if mini > test:
                best = i
                mini = test
        return best

    def getSamples(self, start):
        samples = []
        samples.append(start)
        for i in range(start, cnsts.RX_LEN, 10):
            samples.append(i)
        return samples

    def findPacket(self):
        for i in range(0, cnsts.RX_LEN-(5*5*8)):
            pay = []
            for j in range(5):
                stride = []
                start = i + (j*8*5)
                stop = start + (8*5)
                for k in range(start,stop,5):
                    stride.append(self.data[k])
                pay.append(stride)

            found = True
            if (pay[0] != [0,1,1,0,1,0,1,0]):
                found = False
            #for j in range(0,8):
            #    xor =   pay[1][j] ^\
            #            pay[2][j] ^\
            #            pay[3][j]
            #    if pay[4][j] != xor:
            #        found = False
            if found:
                print(i)
                print(pay)
                print("pay")

    def plot(self, name):
        #plt.subplot(2,1,1)
        plt.plot(self.data)
        #plt.subplot(2,1,2)

        p = self.findSamplePhase()
        s = self.getSamples(p+5)

        y = [0.5] * len(s)
        plt.scatter(s,y)


        #plt.scatter(self.cntPre(0.0076, 5.0075), 0)

        plt.show()
