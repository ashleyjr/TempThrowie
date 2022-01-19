import numpy as np
from throwieTransmission import throwieTransmission

with open("throwie_20220119_194731.log", "r") as f:
    data=f.read().splitlines()[0]
    f.close()

u = throwieTransmission(data)
u.findPacket()

#u.sweep()
u.plot("graph.png")
