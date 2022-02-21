import serial
import string
import os
from datetime import datetime
from throwieConstants import throwieConstants as cnsts


if __name__ == "__main__":
    with serial.Serial('/dev/ttyUSB0', cnsts.BAUDRATE, timeout=0.1) as ser:
        while True:
            s = ser.read(cnsts.RX_LEN)
            if len(s) == cnsts.RX_LEN:
                d = datetime.now()
                name = d.strftime(f"{cnsts.LOGDIR}/throwie_%Y%m%d_%H%M%S.log")
                if not os.path.exists(cnsts.LOGDIR):
                    os.makedirs(cnsts.LOGDIR)
                with open(name, "w") as f:
                    f.write(s.decode("utf-8") )
                    f.close()

