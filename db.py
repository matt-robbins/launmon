import sqlite3
import datetime
import os
from contextlib import closing


class LaundryDb:
    def __init__(self, path="laundry.db"):
        self.path = os.getenv("LAUNMON_DB_PATH", path)
        self.create(
            """
            CREATE TABLE IF NOT EXISTS events 
            (location TEXT, status TEXT, time TIMESTAMP)
            """
        )
        self.create(
            """
            CREATE TABLE IF NOT EXISTS rawcurrent 
            (location TEXT, current REAL, time TIMESTAMP)
            """
        )
        self.create(
            """
            CREATE TABLE IF NOT EXISTS locations 
            (location TEXT UNIQUE, nickname TEXT, 
            tzoffset INT, lastseen TIMESTAMP)
            """
        )
        self.create(
            """
            CREATE TABLE IF NOT EXISTS calibration 
            (location TEXT UNIQUE, calibration REAL)
            """
        )
        self.create(
            """
            CREATE TABLE IF NOT EXISTS subscriptions
            (endpoint TEXT, location TEXT, subscription TEXT,
            UNIQUE(endpoint,location))
            """
        )

    def insert(self, query, args):
        with closing(sqlite3.connect(self.path)) as con:
            with closing(con.cursor()) as cur:
                cur.execute(query, args)
            con.commit()

    def create(self, query):
        with closing(sqlite3.connect(self.path)) as con:
            with closing(con.cursor()) as cur:
                cur.execute(query)
            con.commit()

    def fetch(self, query, args=()):
        ret = None
        with closing(sqlite3.connect(self.path)) as con:
            with closing(con.cursor()) as cur:
                ret = cur.execute(query, args).fetchall()
        return ret

    def addEvent(self, location, status, time=datetime.datetime.utcnow()):
        sqlt = """INSERT INTO events VALUES (?, ?, ?);"""
        self.insert(sqlt, (location, status, time))

    def addCurrentReading(self, location, value, time=datetime.datetime.utcnow()):
        sqlt = """INSERT INTO rawcurrent VALUES (?, ?, ?);"""
        self.insert(sqlt, (location, value, time))
        sqlt = """
        INSERT INTO locations (location,lastseen) VALUES (:loc,:ts)
        ON CONFLICT (location) DO UPDATE SET lastseen=:ts;
        """
        self.insert(sqlt, {"loc": location, "ts": time})

    def getLatest(self):
        sqlt = """SELECT e.location, e.status, e.time, l.lastseen, l.nickname FROM events e
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
        return self.fetch(sqlt, (location,))

    def getHist(self, location="1", weekday=0):
        sqlt = """SELECT 
            cast(strftime('%H',datetime(time, :tzoff || ' hour')) as INT) hour, 
            count(*)/12. perhour 
            FROM events 
            WHERE time > datetime('now','-28 day') 
            AND cast(strftime('%w',datetime(time, :tzoff || ' hour')) as INT) = :wkday 
            AND location=:loc
            GROUP BY hour;"""

        d = self.fetch(sqlt, {"tzoff": "-5", "wkday": weekday, "loc": location})

        b = [0 for ix in range(24)]
        for bin, val in d:
            b[bin] = val

        return b

    def getEvents(self, location="all", hours=-24):
        if location == "all" or location is None:
            return self.fetch(
                """
                SELECT time, status 
                FROM events 
                WHERE time > datetime('now', ? || ' hours')""",
                (-hours,),
            )
        else:
            return self.fetch(
                """
                SELECT time, status 
                FROM events 
                WHERE time > datetime(
                    (SELECT max(time) FROM events), ? || ' hours')
                AND location = ?;
                """,
                (-hours, location),
            )

    def getWashCycles(self, location="1", hours=-24):
        sqlt = """
            SELECT time,endtime FROM (
                SELECT time,lead(time) OVER (ORDER BY time) endtime,cstart FROM (
                    SELECT time,
                        (lag(status) OVER (ORDER BY time) || status) 
                            IN ('nonewash','noneboth','dryboth','drywash') cstart, 
                        (lag(status) OVER (ORDER BY time) || status) 
                            IN ('washnone','bothnone','bothdry','washdry') cend
                    FROM events 
                    WHERE location = ? AND time > datetime('now', ? || ' hours')) 
                WHERE cstart > 0 OR cend > 0)
            WHERE cstart > 0
        """
        return self.fetch(sqlt, (location, -hours))

    def getDryCycles(self, location="1", hours=-24):
        sqlt = """
            SELECT time,endtime FROM (
                SELECT time,lead(time) OVER (ORDER BY time) endtime,cstart FROM (
                    SELECT time,
                        (lag(status) OVER (ORDER BY time) || status) 
                            IN ('nonedry','noneboth','washboth','washdry') cstart, 
                        (lag(status) OVER (ORDER BY time) || status) 
                            IN ('drynone','bothnone','bothwash','drywash') cend
                    FROM events 
                    WHERE location = ? AND time > datetime('now', ? || ' hours')) 
                WHERE cstart > 0 OR cend > 0)
            WHERE cstart > 0
        """
        return self.fetch(sqlt, (location, -hours))

    def getCurrent(self, location="1", minutes=-60):
        return self.fetch(
            """
            SELECT location, current, strftime('%H:%M:%S', time) 
            FROM rawcurrent 
            WHERE time > datetime(
                (SELECT max(time) FROM rawcurrent), ? || ' minutes'
            ) 
            AND location = ?
            """,
            (-minutes, location),
        )

    def getCurrentRange(self, location="1", start="", end=""):
        sqlt = """
        SELECT location,current,strftime('%H:%M:%S',time) 
            FROM rawcurrent 
            WHERE time > ?
            AND time < ?
            AND location = ?
        """
        return self.fetch(sqlt, (start, end, location))
    
    def getName(self,location="1"):
        sqlt = """
            SELECT coalesce(nickname, location) FROM locations WHERE location = ? LIMIT 1
        """
        return self.fetch(sqlt, (location,))[0][0]
    
    def getNames(self):
        sqlt = """
            SELECT coalesce(nickname, location) FROM locations ORDER BY location;
        """
        return [n[0] for n in self.fetch(sqlt)]
    
    def insertSubscription(self,endpoint="",location="1",subscription=""):
        sqlt = """
        INSERT OR IGNORE INTO subscriptions (endpoint,location,subscription) 
        VALUES (:ep,:loc,:sub)
        ;"""

        self.insert(sqlt, {"ep": endpoint, "loc": location, "sub": subscription})

    def getSubscriptions(self,location="1"):
        if location == "all" or location is None:
            return self.fetch("SELECT subscription FROM subscriptions") 
        else:
            return self.fetch("SELECT subscription FROM subscriptions WHERE location = ?", location)

    def checkSubscription(self,endpoint=""):
        r = self.fetch(
            "SELECT location FROM subscriptions WHERE endpoint = ?", (endpoint,))
        return [v[0] for v in r]

    def deleteSubscription(self,endpoint="", location=""):
        sqlt = """DELETE FROM subscriptions 
            WHERE endpoint = ? AND
            location = ?;"""
        self.insert(sqlt,(endpoint,location))

    

if __name__ == "__main__":
    db = LaundryDb()

    print(db.getWashCycles("4", 48))

    pass
