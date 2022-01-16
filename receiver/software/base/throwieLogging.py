import serial
from datetime import datetime


with serial.Serial('/dev/ttyUSB0', 115200, timeout=5) as ser:
    while True:
        s = ser.read(1)
        d = datetime.now()
        if(s == '\n'):
            rx = ser.read(4096)
            name = d.strftime("throwie_%Y%m%d_%H%M%S.log")
            with open(name, "w") as f:
                f.write(rx)
                f.close()

