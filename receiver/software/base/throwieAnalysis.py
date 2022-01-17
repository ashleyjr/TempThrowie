from throwieTransmission import throwieTransmission

with open("throwie_20220116_230012.log", "r") as f:
    data=f.read().splitlines()[0]
    f.close()

u = throwieTransmission(data)

for i in range(10):
    print(u.cntPre(i))


u.plot("graph.png")
