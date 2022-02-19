from throwieConstants import throwieConstants as cnsts
import glob
import pickle
import os
import argparse

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
                    self.db[cnsts.rxToId(rx)].append({
                        'year' : cnsts.pathToYear(l),
                        'month': cnsts.pathToMonth(l),
                        'day'  : cnsts.pathToDay(l),
                        'hour' : cnsts.pathToHour(l),
                        'temp' : cnsts.rxToTemp(rx),
                        'batt' : cnsts.rxToBattery(rx)
                    })
                except:
                    print(f"Log file{l} corrupt")
            os.remove(l)

    def __graphDay(self, filename, dt, key):
        for i in range(len(self.db)):
            if len(self.db[i]) > 0:
                data = []
                hour = []
                for e in self.db[i]:
                    if  (dt.year == e['year']) and\
                        (dt.month == e['month']) and \
                        (dt.day == e['day']):
                        hour.append(e['hour'])
                        data.append(e[key])
                data = [x for _,x in sorted(zip(hour,data))]
                hour = sorted(hour)
                plt.plot(hour, data)
        plt.savefig(filename, dpi=200)
        plt.close()

    def graphBattery(self, dt):
        self.__graphDay(dt.strftime("graph_battery_%Y%m%d.png"), dt, 'batt')

    def graphTemp(self, dt):
        self.__graphDay(dt.strftime("graph_temp_%Y%m%d.png"), dt, 'temp')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--update', action='store_true')     
    parser.add_argument('--loop', action='store_true')     
    parser.add_argument('--plottoday', action='store_true')
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

    if args['plottoday']:
        import matplotlib.pyplot as plt
        import datetime
        u.graphTemp(datetime.datetime.today())
        u.graphBattery(datetime.datetime.today())
