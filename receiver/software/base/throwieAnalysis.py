import numpy as np
from throwieTransmission import throwieTransmission
import glob

# List all log files
logfiles = []
for l in glob.glob("*.log"):
    logfiles.append(l)

# Open each log file
for log in logfiles:
    with open(log, "r") as f:
        data=f.read().splitlines()[0]
        f.close()

    u = throwieTransmission(data)
    u.findPacket()

#u.sweep()
#u.plot("graph.png")
