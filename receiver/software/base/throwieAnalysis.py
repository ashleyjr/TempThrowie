import numpy as np
from throwieReception import throwieReception
from throwieTransmission import throwieTransmission
import glob
import matplotlib.pyplot as plt

# List all log files
logfiles = []
for l in glob.glob("*.log"):
    logfiles.append(l)

# Analyse
ur = throwieReception(logfiles)
ur.process()
ur.plot("rx_histogram.png")

# Open each log file
for log in logfiles:
    with open(log, "r") as f:
        data=f.read().splitlines()[0]
        f.close()
    print(log)
    u = throwieTransmission(data)
    print(u.getDeltas())
    u.plot(log.replace(".log","_raw.png"), u.getData())
    u.plot(log.replace(".log","_fft.png"), u.fft())
    u.plot(log.replace(".log","_filter.png"), u.filter())
    u.hist(log.replace(".log","_hist.png"), u.getDeltas())
