from throwieConstants import throwieConstants as cnsts
import glob
import pickle
import os
import sys

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
        print(f"{l}: ID={iden}, Temp={temp}, Battery={batt}")
        db[iden].append({
            'time' : l,
            'temp' : temp,
            'batt' : batt
        })
        os.remove(l)

# Print the DB
for i in range(len(db)):
    if len(db[i]) > 0:
        print(f"ID={i}")
        for e in db[i]:
            print(f"\tTime = {e['time']}")
            print(f"\t\tTemp    = {e['temp']}C")
            print(f"\t\tBattery = {e['batt']}V")
# Write DB
with open(cnsts.DBNAME, 'wb') as f:
    pickle.dump(db, f)

