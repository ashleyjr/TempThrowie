from throwieConstants import throwieConstants as cnsts
import matplotlib.pyplot as plt

class throwieTransmission():

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

    def cntPre(self, phase):
        i = phase
        p = self.data[i]
        c = 0
        while i < cnsts.RX_LEN:
            i += 5
            p = 0 if (p == 1) else 1
            if self.data[i] != p:
                return c
            c += 1

    def plot(self, name):
        plt.plot(self.data)

        for i in range(5):
            plt.scatter(self.cntPre(i), 0)

        plt.show()
