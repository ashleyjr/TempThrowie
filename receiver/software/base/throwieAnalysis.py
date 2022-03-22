from throwieConstants import throwieConstants as cnsts
import glob
import pickle
import os
import argparse
import math
import datetime
import sqlite3
import logging

class throwieAnalysis:

    def __init__(self):
        """
        Open DB if it exists or create
        a new one
        """
        self.__start = datetime.datetime.now()
        con = sqlite3.connect(cnsts.DBNAME)
        self.__cur = con.cursor()

    def initLog(self, logname):
        self.__logger = logging.getLogger(logname)
        self.__logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(logname, mode='w')
        fmt = logging.Formatter('[%(asctime)s] : %(message)s')
        fh.setFormatter(fmt)
        self.__logger.addHandler(fh)
        self.__logger.info(f"Start")
    
    def endLog(self):
        delta = datetime.datetime.now() - self.__start
        self.__logger.info(f"Elapsed {delta.total_seconds()}s")
        self.__logger.info(f"End")
 
    def logStats(self):
        self.__logger.info(f"Unique IDs : {self.getUniqueIds()}")
        date = self.getFirstDate()
        time = self.getFirstTime(date)
        self.__logger.info(f"First Rx : Date = {date}, Time = {time}")
        date = self.getLastDate()
        time = self.getLastTime(date)
        self.__logger.info(f"Last Rx  : Date = {date}, Time = {time}")

    def getUniqueIds(self):
        cmd = f"SELECT DISTINCT id FROM throwie"
        self.__cur.execute(cmd)
        ids = []
        for row in self.__cur.fetchall():
            ids.append(int(row[0]))
        return sorted(ids)

    def getIds(self, idet):
        cmd = f"SELECT * FROM throwie WHERE id='{idet}'"
        self.__cur.execute(cmd)
        return self.__cur.fetchall()

    def numIds(self, idet):
        return len(self.getIds(idet))

    def hasId(self, idet):
        return self.numIds() > 0
    
    def getUniqueDates(self):
        cmd = f"SELECT DISTINCT date FROM throwie"
        self.__cur.execute(cmd)
        dates = []
        for row in self.__cur.fetchall():
            dates.append(int(row[0]))
        return sorted(dates)
     
    def getFirstDate(self):
        return self.getUniqueDates()[0]

    def getLastDate(self):
        return self.getUniqueDates()[-1]
    
    def getTimes(self, date):
        cmd = f"SELECT time FROM throwie WHERE date='{date}'"
        self.__cur.execute(cmd)
        times = []
        for row in self.__cur.fetchall():
            times.append(int(row[0]))
        return sorted(times)
     
    def getLastTime(self, date):
        return self.getTimes(date)[-1]  

    def getFirstTime(self, date):
        return self.getTimes(date)[0]  

    def __getDay(self, idet, dt, key):
        data = []
        hour = []
        dt_str = dt.strftime("%Y%m%d")
        cmd = f"SELECT time, {key} FROM throwie WHERE date='{dt_str}' AND id='{idet}'"
        self.__cur.execute(cmd)
        for t, k in self.__cur.fetchall():
            then = datetime.datetime.strptime(str(t), '%H%M%S')
            start = then.replace(hour=0, minute=0, second=0)
            h=(then-start).total_seconds() / 3600
            hour.append(h)
            data.append(float(k))
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
        for i in self.getUniqueIds():
            hour, data = self.__getDay(i, dt, key)
            plt.scatter(hour, data)
        if key == 'batt':
            plt.ylabel("Voltage (V)")
            plt.title("Battery Voltage")
        else:
            plt.ylabel("Temperature (C)")
            plt.title("Temperature")
        plt.grid()
        plt.xticks(range(0, 25))
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
            plt.xticks(np.arange(0, 25, 1))
            plt.xlabel("Time (Hours)")
        plt.grid()
        plt.savefig(filename, dpi=150)
        plt.close()

    def __graphRxDeltas(self, filename, then):
        for i in range(len(self.db)):
            if self.__dbHasId(i):
                ds = []
                for e in self.db[i]:
                    if e['datetime'] > then:
                        ds.append((e['datetime'] - then).total_seconds())
                ds = sorted(ds)
                d = []
                for i in range(1,len(ds)):
                    d.append(ds[i]-ds[i-1])
                plt.hist(d)
        plt.ylabel("Count")
        plt.title("Rx Intervals")
        plt.yscale('log')
        plt.grid()
        plt.xlabel("Interval (Seconds)")
        plt.savefig(filename, dpi=150)
        plt.close()

    def graphBattery(self, out, dt):
        self.__graphDay(out, dt, 'batt')

    def graphTemp(self, out, dt):
        self.__graphDay(out, dt, 'temp')

    def graphBatterySince(self, dt):
        self.__graphSince(dt.strftime("graph_battery_since_%Y%m%d.png"), dt, 'batt')

    def graphTempSince(self, dt):
        self.__graphSince(out, dt, 'temp')

    def graphRxDeltasSince(self, dt):
        self.__graphRxDeltas(dt.strftime("graph_deltas_since_%Y%m%d.png"), dt)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--plotdate',       type=str)
    parser.add_argument('--plotsince',      type=str)
    parser.add_argument('--plotdeltas',     type=str)
    parser.add_argument('--stats',          action='store_true')
    parser.add_argument('--plottemptoday',  action='store_true')
    parser.add_argument('--plotbatttoday',  action='store_true')
    parser.add_argument('--out',            type=str)
    parser.add_argument('--log',            type=str)

    args = vars(parser.parse_args())

    u = throwieAnalysis()
    
    u.initLog(f"{args['log'].replace('.log','')}.log")

    out = args['out']

    if args['plotbatttoday'] or \
        args['plottemptoday'] or \
        (args['plotdeltas'] is not None) or\
        (args['plotdate'] is not None) or\
        (args['plotsince'] is not None):
        import matplotlib.pyplot as plt
        import numpy as np

    if args['stats']:
        u.logStats()

    if args['plottemptoday']:
        u.graphTemp(out, datetime.datetime.today())
    
    if args['plotbatttoday']:
        u.graphBattery(out, datetime.datetime.today())

    if args['plotdeltas']:
        dt = datetime.datetime.strptime(args['plotdeltas'], '%Y%m%d')
        u.graphRxDeltasSince(dt)

    if (args['plotdate'] is not None):
        dt = datetime.datetime.strptime(args['plotdate'], '%Y%m%d')
        u.graphTemp(dt)
        u.graphBattery(dt)

    if (args['plotsince'] is not None):
        dt = datetime.datetime.strptime(args['plotsince'], '%Y%m%d')
        u.graphTempSince(dt)
        u.graphBatterySince(dt)

    u.endLog()

