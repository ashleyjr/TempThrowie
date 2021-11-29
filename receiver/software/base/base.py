from BaseConstants import BaseConstants as c
import sqlite3

class Record:

    def write(self, s):
        con = sqlite3.connect(c.DBNAME)
        cur = con.cursor()
        cur.execute("create table if not exists "+c.TBLNAME+" (date text, data text)")
        cur.execute("INSERT INTO "+c.TBLNAME+" VALUES ('"+s+"', '"+s+"')")
        con.commit()
        con.close()


def main():
    u = Record()
    u.write("Test")


if "__main__" == __name__:
    main()
