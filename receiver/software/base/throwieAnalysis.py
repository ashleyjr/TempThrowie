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

    u = throwieTransmission(data)
    #print(len(u.getData()))
    #print(u.getMean())
    #print(u.getMan())
    print(u.decode())
    #u.plot(log.replace(".log","_raw.png"), u.getData())
    #u.plot(log.replace(".log","_start.png"), u.getData(50))
    #u.plot(log.replace(".log","_mean.png"), u.getMean()[0:64])
    #u.plot(log.replace(".log","_man.png"), u.getMan())
    #u.plot(log.replace(".log","_fft.png"), u.fft())
    #u.plot(log.replace(".log","_filter.png"), u.filter())
    #u.hist(log.replace(".log","_hist.png"), u.getDeltas())
