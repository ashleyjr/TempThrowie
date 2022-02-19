from throwieConstants import throwieConstants as cnsts
import glob
import pickle
import os
import sys
import matplotlib.pyplot as plt

# Open DB
if os.path.isfile(cnsts.DBNAME):
    # Open the exisiting DB
    with open(cnsts.DBNAME, 'rb') as f:
        db = pickle.load(f)
else:
    # Create a new DB
    db = []
    for i in range(256):
        db.append([])

# Inspect each log file and add to db
for l in glob.glob("*.log"):
    with open(l, 'r') as f:
        rx = f.read()
        iden = int(rx[0:2], 16)
        temp = (int(rx[2:4], 16) / 4) - 10
        batt = (int(rx[4:6], 16) * (3.3/256))/ 0.471
        hours = int(l[17:19])
        minutes = int(l[19:21])
        seconds = int(l[21:23])
        hour = hours + (float(minutes) / 60) + (float(seconds) / 3600)
        db[iden].append({
            'day'  : l[8:16],
            'hour' : hour,
            'temp' : temp,
            'batt' : batt
        })
        print(f"{l}: ID={iden}, Hour={hour}, Temp={temp}, Battery={batt}")

        os.remove(l)

# Print the DB
#for i in range(len(db)):
#    if len(db[i]) > 0:
#        print(f"ID={i}")
#        for e in db[i]:
#            print(f"\tTime = {e['time']}")
#            print(f"\t\tTemp    = {e['temp']}C")
#            print(f"\t\tBattery = {e['batt']}V")
# Write DB
with open(cnsts.DBNAME, 'wb') as f:
    pickle.dump(db, f)


# Plot all temps
for i in range(len(db)):
    if len(db[i]) > 0:
        temp = []
        hour = []
        for e in db[i]:
            hour.append(e['hour'])
            temp.append(e['temp'])
        temp = [x for _,x in sorted(zip(hour,temp))]
        hour = sorted(hour)
        plt.plot(hour, temp)

plt.savefig("temp_graph.png", dpi=200)
plt.close()


# Plot all battery
for i in range(len(db)):
    if len(db[i]) > 0:
        batt = []
        hour = []
        for e in db[i]:
            hour.append(e['hour'])
            batt.append(e['batt'])
        temp = [x for _,x in sorted(zip(hour,batt))]
        hour = sorted(hour)
        plt.plot(hour, batt)

plt.savefig("batt_graph.png", dpi=200)
plt.close()
