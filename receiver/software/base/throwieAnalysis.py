import numpy as np
from throwieTransmission import throwieTransmission
import glob
import matplotlib.pyplot as plt

# List all log files
logfiles = []
for l in glob.glob("*.log"):
    logfiles.append(l)

# Count log files
print("Num log files: {}".format(len(logfiles)))

# Histogram of reception separations
rx_times = []
for log in logfiles:
    rx_time = int(log[21:23])
    rx_time += 60*int(log[19:21])
    rx_time += 60*60*int(log[17:19])
    rx_times.append(rx_time)
rx_times.sort()
print(rx_times)

deltas=[]
for i in range(0,len(rx_times)-1):
    # When wraps around a day
    if rx_times[i] > rx_times[i+1]:
        d = (24*60*60)
    else:
        d = 0
    d += (rx_times[i+1] - rx_times[i])
    deltas.append(d)
print(deltas)
plt.hist(deltas)
plt.show()

# Open each log file
for log in logfiles:
    with open(log, "r") as f:
        data=f.read().splitlines()[0]
        f.close()

    u = throwieTransmission(data)
    u.findPacket()

#u.sweep()
#u.plot("graph.png")
