import serial
from datetime import datetime

with serial.Serial('/dev/ttyUSB0', 115200, timeout=5) as ser:
    with open("filter.log", "w") as f:
        for i in range(int(5e4)):
            rx = ser.read(1)
            f.write(rx)
        f.close()

