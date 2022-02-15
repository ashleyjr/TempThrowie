import serial
import string
from datetime import datetime
from throwieConstants import throwieConstants as cnsts

with serial.Serial('/dev/ttyUSB0', cnsts.BAUDRATE) as ser:
    while True:
        s = ser.read(cnsts.RX_LEN)
        d = datetime.now()
        name = d.strftime("throwie_%Y%m%d_%H%M%S.log")
        with open(name, "w") as f:
            f.write(s)
            f.close()

