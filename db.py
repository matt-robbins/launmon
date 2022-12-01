import sqlite3
import datetime
from contextlib import closing

class LaundryDb:
    def __init__(self, path="laundry.db"):
        self.path = path
        self.create("CREATE TABLE IF NOT EXISTS events (location TEXT, status TEXT, time TIMESTAMP)")
        self.create("CREATE TABLE IF NOT EXISTS rawcurrent (location TEXT, current REAL, time TIMESTAMP)")

    def insert(self,query, args):
        with closing(sqlite3.connect(self.path)) as con:
            with closing(con.cursor()) as cur:
                cur.execute(query, args)
            con.commit()
    def create(self, query):
        with closing(sqlite3.connect(self.path)) as con:
            with closing(con.cursor()) as cur:
                cur.execute(query)
            con.commit()
    def fetch(self,query):
        ret = None
        with closing(sqlite3.connect(self.path)) as con:
            with closing(con.cursor()) as cur:
                ret = cur.execute(query).fetchall()
        return ret

    def addEvent(self,location,status,time=datetime.datetime.utcnow()):
        sqlt = """INSERT INTO events VALUES (?, ?, ?);"""
        self.insert(sqlt,(location,status,time))

    def addCurrentReading(self,location,value,time=datetime.datetime.utcnow()):
        sqlt = """INSERT INTO rawcurrent VALUES (?, ?, ?);"""
        self.insert(sqlt,(location,value,time))

    def getLatest(self):
        sqlt = """SELECT e.location, e.status, e.time FROM events e
                INNER JOIN (
                    SELECT location, max(time) as MaxDate 
                    FROM events 
                    GROUP BY location
                ) em on e.location = em.location AND e.time = em.MaxDate
                ORDER BY e.location"""
        return self.fetch(sqlt)

if (__name__ == "__main__"):
    db = LaundryDb()

    db.addEvent('4','dry',datetime.datetime.fromtimestamp(0))
    db.addEvent('2','both',datetime.datetime.fromtimestamp(0))
    db.addEvent('4','none',datetime.datetime.utcnow())

    print(db.getLatest())

    pass