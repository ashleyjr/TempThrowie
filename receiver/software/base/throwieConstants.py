
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

    def pathToYear(path):
        return int(path[13:17])

    def pathToMonth(path):
        return int(path[17:19])

    def pathToDay(path):
        return int(path[19:21])

    def pathToHour(path):
        hours = int(path[22:24])
        minutes = int(path[24:26])
        seconds = int(path[26:28])
        hour = round((hours + (float(minutes) / 60) + (float(seconds) / 3600)),2)
        return hour
