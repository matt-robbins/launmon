import sqlite3
import datetime
from contextlib import closing

class LaundryDb:
    def __init__(self, path="laundry.db"):
        self.path = path
        self.create("CREATE TABLE IF NOT EXISTS events (location TEXT, status TEXT, time TIMESTAMP)")
        self.create("CREATE TABLE IF NOT EXISTS rawcurrent (location TEXT, current REAL, time TIMESTAMP)")
        self.create("CREATE TABLE IF NOT EXISTS locations (location TEXT UNIQUE, nickname TEXT, tzoffset INT, lastseen TIMESTAMP)")
        self.create("CREATE TABLE IF NOT EXISTS calibration (location TEXT UNIQUE, calibration REAL)")

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
    def fetch(self,query,args=()):
        ret = None
        with closing(sqlite3.connect(self.path)) as con:
            with closing(con.cursor()) as cur:
                ret = cur.execute(query,args).fetchall()
        return ret

    def addEvent(self,location,status,time=datetime.datetime.utcnow()):
        sqlt = """INSERT INTO events VALUES (?, ?, ?);"""
        self.insert(sqlt,(location,status,time))

    def addCurrentReading(self,location,value,time=datetime.datetime.utcnow()):
        sqlt = """INSERT INTO rawcurrent VALUES (?, ?, ?);"""
        self.insert(sqlt,(location,value,time))
        sqlt = "INSERT INTO locations(location,lastseen) VALUES (:loc,:ts) ON CONFLICT(location) DO UPDATE SET lastseen=:ts;"
        self.insert(sqlt,{'loc':location,'ts':time})

    def getLatest(self):
        sqlt = """SELECT e.location, e.status, e.time, l.lastseen FROM events e
                INNER JOIN (
                    SELECT location, max(time) as MaxDate 
                    FROM events 
                    GROUP BY location
                ) em on e.location = em.location AND e.time = em.MaxDate
                JOIN locations l ON l.location = e.location
                ORDER BY e.location"""
        return self.fetch(sqlt)

    def getLastSeen(self):
        sqlt = """SELECT location, lastseen FROM locations;"""
        return self.fetch(sqlt)

    def getCal(self, location="1"):
        sqlt = "SELECT calibration FROM calibration WHERE location = ?;"
        return self.fetch(sqlt,(location,))

    def getHist(self, location="1",weekday=0):

        sqlt = """SELECT 
            cast(strftime('%H',datetime(time, :tzoff || ' hour')) as INT) hour, 
            count(*)/12. perhour 
            FROM events 
            WHERE time > datetime('now','-28 day') 
            AND cast(strftime('%w',datetime(time, :tzoff || ' hour')) as INT) = :wkday 
            AND location=:loc
            GROUP BY hour;"""
        
        d = self.fetch(sqlt,{'tzoff':"-5",'wkday':weekday,'loc':location})
        
        b = [0 for ix in range(24)]
        for bin,val in d: 
            b[bin] = val
        
        return b



    def getEvents(self, location="all", hours=-24):
        if (location=="all" or location is None):
            return self.fetch("SELECT time,status FROM events WHERE time > datetime('now', ? || ' hours')", (-hours,))
        else:
            return self.fetch("SELECT time,status FROM events WHERE time > datetime('now', ? || ' hours') AND location = ?;", (-hours, location))


if (__name__ == "__main__"):
    db = LaundryDb()

    db.addEvent('4','dry',datetime.datetime.fromtimestamp(0))
    db.addEvent('2','both',datetime.datetime.fromtimestamp(0))
    db.addEvent('4','none',datetime.datetime.utcnow())

    print(db.getLatest())
    print(db.getHist(None))

    print(db.getEvents('2',96))

    pass