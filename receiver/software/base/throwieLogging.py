import serial
import string
import os
import sys
from datetime import datetime as dt
from throwieConstants import throwieConstants as cnsts
import sqlite3
import argparse
import logging
import threading
import time

class throwieLogging:

    def __init__(self, log_level):
        # Variables
        self.__uart_max_buf = 0
        self.__uart_data_buf = []
        self.__uart_datetime_buf = []

        # Start threads
        self.__uart_rx = threading.Thread(target=self.__uartRx)
        self.__write_db = threading.Thread(target=self.__writeDb)
        self.__uart_rx.start()
        self.__write_db.start()

        # Configure logging
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(log_level)
        fh = logging.FileHandler(cnsts.LOGNAME, mode='w')
        fmt = logging.Formatter('[%(asctime)s] : %(message)s')
        fh.setFormatter(fmt)
        self.__logger.addHandler(fh)
        self.__logger.info('Started')

    def __uartRx(self):
        with serial.Serial('/dev/ttyUSB0', cnsts.BAUDRATE, timeout=0.1) as ser:
            while True:
                s = ser.read(cnsts.RX_LEN)
                if len(s) == cnsts.RX_LEN:
                    self.__uart_data_buf.append(s.decode("utf-8"))
                    self.__uart_datetime_buf.append(dt.now())
                    if len(self.__uart_data_buf) > self.__uart_max_buf:
                        self.__uart_max_buf = len(self.__uart_data_buf)
                        self.__logger.info(f"UART buffer reached new fill level of {self.__uart_max_buf}")

    def __writeDb(self):
        while True:
            time.sleep(cnsts.DB_UPD_S)

            # Open database admin
            con = sqlite3.connect(cnsts.DBNAME)
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS throwie (date text, time text, id text, temp text, batt text)")

            # Drain buffer
            fill = len(self.__uart_data_buf)
            for i in range(fill):
                then = self.__uart_datetime_buf.pop(0)
                d = then.strftime("%Y%m%d")
                t = then.strftime("%H%M%S")
                data = self.__uart_data_buf.pop(0)
                idet = cnsts.rxToId(data)
                temp = cnsts.rxToTemp(data)
                batt = cnsts.rxToBattery(data)
                # SQL command
                cmd = f"INSERT INTO throwie VALUES ('{d}','{t}','{idet}','{temp}','{batt}')"
                cur.execute(cmd)
                self.__logger.debug(cmd)

            # Close database admin
            con.commit()
            con.close()


def test_reads(name):
    import time
    for i in range(100):
        con = sqlite3.connect('example.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM throwie WHERE temp='27'")
        rows = cur.fetchall()
        for row in rows:
            print(row)
        time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true')
    args = vars(parser.parse_args())

    u = throwieLogging(logging.INFO)

