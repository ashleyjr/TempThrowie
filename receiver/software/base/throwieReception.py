from throwieConstants import throwieConstants as cnsts
import matplotlib.pyplot as plt

class throwieReception:

    def __init__(self, logfiles):
        self.logfiles = logfiles

    def process(self):

        # Count log files
        print("Num log files: {}".format(len(self.logfiles)))

        # Histogram of reception separations
        rx_times = []
        for log in self.logfiles:
            rx_time = int(log[21:23])
            rx_time += 60*int(log[19:21])
            rx_time += 60*60*int(log[17:19])
            rx_times.append(rx_time)
        rx_times.sort()
        print(rx_times)

        self.deltas=[]
        for i in range(0,len(rx_times)-1):
            # When wraps around a day
            if rx_times[i] > rx_times[i+1]:
                d = (24*60*60)
            else:
                d = 0
            d += (rx_times[i+1] - rx_times[i])
            self.deltas.append(d)

    def plot(self, name):
        plt.hist(self.deltas)
        plt.savefig(name, dpi=150)
        plt.close()


