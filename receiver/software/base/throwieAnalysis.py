from throwieConstants import throwieConstants as cnsts
import glob
import pickle
import os
import argparse
import math
import datetime

class throwieAnalysis:

    def __init__(self):
        """
        Open DB if it exists or create
        a new one
        """
        if os.path.isfile(cnsts.DBNAME):
            with open(cnsts.DBNAME, 'rb') as f:
                self.db = pickle.load(f)
        else:
            self.db = []
            for i in range(cnsts.MAX_THROWIES):
                self.db.append([])

    def writeDb(self):
        """
        Write DB
        """
        with open(cnsts.DBNAME, 'wb') as f:
            pickle.dump(self.db, f)

    def addLogs(self):
        """
        Inspect each log file and add to db
        """
        logs = glob.glob(cnsts.LOGS)
        for l in logs:
            with open(l, 'r') as f:
                try:
                    rx = f.read()
                    dt = datetime.datetime.strptime(cnsts.pathDateTime(l), '%Y%m%d_%H%M%S')
                    self.db[cnsts.rxToId(rx)].append({
                        'datetime' : dt,
                        'temp' : cnsts.rxToTemp(rx),
                        'batt' : cnsts.rxToBattery(rx)
                    })
                except:
                    print(f"Log file{l} corrupt")
            os.remove(l)

    def __dbHasId(self, ident):
        return len(self.db[ident]) > 0

    def __getDay(self, ident, dt, key):
        data = []
        hour = []
        for e in self.db[ident]:
            if(dt.date() == e['datetime'].date()):
                start = e['datetime'].replace(hour=0, minute=0, second=0)
                h=(e['datetime']-start).total_seconds() / 3600
                hour.append(h)
                data.append(e[key])
        data = [x for _,x in sorted(zip(hour,data))]
        hour = sorted(hour)
        return hour, data

    def __getSince(self, ident, then, key):
        data = []
        hour = []
        for e in self.db[ident]:
            if  e['datetime'] > then:
                h = (e['datetime'] - then).total_seconds() / 3600
                hour.append(h)
                data.append(e[key])
        data = [x for _,x in sorted(zip(hour,data))]
        hour = sorted(hour)
        time = []
        if max(hour) > 24:
            for h in hour:
                time.append(h/24)
        else:
            time = hour
        return time, data

    def __graphDay(self, filename, dt, key):
        for i in range(len(self.db)):
            if self.__dbHasId(i):
                hour, data = self.__getDay(i, dt, key)
                plt.scatter(hour, data)
        if key == 'batt':
            plt.ylabel("Voltage (V)")
            plt.title("Battery Voltage")
        else:
            plt.ylabel("Temperature (C)")
            plt.title("Temperature")
        plt.grid()
        plt.xticks(np.arange(0, 24, 1))
        plt.xlabel("Time (Hours)")
        plt.savefig(filename, dpi=150)
        plt.close()

    def __graphSince(self, filename, dt, key):
        m = 0
        for i in range(len(self.db)):
            if self.__dbHasId(i):
                time, data = self.__getSince(i, dt, key)
                plt.scatter(time, data)
                if max(time) > m:
                    m = max(time)
        if key == 'batt':
            plt.ylabel("Voltage (V)")
            plt.title("Battery Voltage")
        else:
            plt.ylabel("Temperature (C)")
            plt.title("Temperature")
        if (datetime.datetime.now() - dt).total_seconds() > (24*60*60):
            plt.xlabel("Time (Days)")
            plt.xticks(np.arange(0, math.ceil(m)+0.25, 0.25))
        else:
            plt.xticks(np.arange(0, 24, 1))
            plt.xlabel("Time (Hours)")
        plt.grid()
        plt.savefig(filename, dpi=150)
        plt.close()

    def graphBattery(self, dt):
        self.__graphDay(dt.strftime("graph_battery_%Y%m%d.png"), dt, 'batt')

    def graphTemp(self, dt):
        self.__graphDay(dt.strftime("graph_temp_%Y%m%d.png"), dt, 'temp')

    def graphBatterySince(self, dt):
        self.__graphSince(dt.strftime("graph_battery_since_%Y%m%d.png"), dt, 'batt')

    def graphTempSince(self, dt):
        self.__graphSince(dt.strftime("graph_temp_since_%Y%m%d.png"), dt, 'temp')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--update',     action='store_true')
    parser.add_argument('--loop',       action='store_true')
    parser.add_argument('--plotdate',   type=str)
    parser.add_argument('--plotsince',  type=str)
    parser.add_argument('--plottoday',  action='store_true')
    args = vars(parser.parse_args())

    u = throwieAnalysis()

    if args['update']:
        while True:
            u.addLogs()
            u.writeDb()
            if args['loop']:
                import time
                time.sleep(10)
            else:
                break
    if args['plottoday'] or \
        (args['plotdate'] is not None) or\
        (args['plotsince'] is not None):
        import matplotlib.pyplot as plt
        import numpy as np

    if args['plottoday']:
        u.graphTemp(datetime.datetime.today())
        u.graphBattery(datetime.datetime.today())

    if (args['plotdate'] is not None):
        dt = datetime.datetime.strptime(args['plotdate'], '%Y%m%d')
        u.graphTemp(dt)
        u.graphBattery(dt)

    if (args['plotsince'] is not None):
        dt = datetime.datetime.strptime(args['plotsince'], '%Y%m%d')
        u.graphTempSince(dt)
        u.graphBatterySince(dt)
