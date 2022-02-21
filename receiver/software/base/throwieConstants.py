
class throwieConstants():

    BAUDRATE     = 115200
    RX_LEN       = 10       # 8 Hex Char + \n + \r
    MAX_THROWIES = 256
    LOGDIR       = "logs"
    LOGS         = f"{LOGDIR}/*.log"
    DBNAME       = f"{LOGDIR}/db.pkl"

    def rxToId(rx):
        return int(rx[0:2], 16)

    def rxToTemp(rx):
        return (int(rx[2:4], 16) / 4) - 10

    def rxToBattery(rx):
        return round(((int(rx[4:6], 16) * (3.3/256))/ 0.471), 2)

    def pathDateTime(path):
        return int(path[13:28])

