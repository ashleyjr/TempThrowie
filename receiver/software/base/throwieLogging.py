import serial
import string
from datetime import datetime
from throwieConstants import throwieConstants as cnsts


if __name__ == "__main__":
    with serial.Serial('/dev/ttyUSB0', cnsts.BAUDRATE) as ser:
        while True:
            s = ser.read(cnsts.RX_LEN)
            d = datetime.now()
            name = d.strftime(f"{cnsts.LOGDIR}/throwie_%Y%m%d_%H%M%S.log")
            with open(name, "w") as f:
                f.write(s.decode("utf-8") )
                f.close()

