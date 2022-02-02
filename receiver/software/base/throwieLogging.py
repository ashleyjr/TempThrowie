import serial
from datetime import datetime
from throwieConstants import throwieConstants as cnsts

with serial.Serial('/dev/ttyUSB0', cnsts.BAUDRATE, timeout=0.1) as ser:
    while True:
        s = ser.read(1)
        d = datetime.now()
        if s in ['0','1']:
            s += ser.read(cnsts.RX_LEN-1)
            d = datetime.now()
            name = d.strftime("throwie_%Y%m%d_%H%M%S.log")
            with open(name, "w") as f:
                f.write(s)
                f.close()

