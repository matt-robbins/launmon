import sqlite3
import os
from contextlib import closing
from cachetools.func import ttl_cache
from datetime import datetime

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
            CREATE TABLE IF NOT EXISTS devices
            (device TEXT UNIQUE, location TEXT, port TEXT, 
            calibration REAL, cal_pow REAL, changed TIMESTAMP)
            """
        )
        self.create(
            """
            CREATE TABLE IF NOT EXISTS calibration 
            (location TEXT UNIQUE, calibration REAL, changed TIMESTAMP)
            """
        )
        self.create(
            """
            CREATE TABLE IF NOT EXISTS subscriptions
            (endpoint TEXT, location TEXT, subscription TEXT,
            UNIQUE(endpoint,location))
            """
        )

        try:
            self.create("""
                ALTER TABLE devices ADD COLUMN cal_pow REAL;
            """)
        except Exception as e:
            pass

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
    
    def getLocations(self):
        return [loc[0] for loc in self.fetch("SELECT location FROM locations;")]

    def addEvent(self, location, status, time=datetime.utcnow()):
        insert = """INSERT INTO events VALUES (?, ?, ?);"""
        self.insert(insert, (location, status, time))

    def addCurrentReading(self, location, value, time=datetime.utcnow()):
        sqlt = """INSERT INTO rawcurrent VALUES (?, ?, ?);"""
        self.insert(sqlt, (location, value, time))
        sqlt = """
            UPDATE locations SET lastseen=:ts WHERE location = :loc;
        """
        self.insert(sqlt, {"loc": location, "ts": time})

    @ttl_cache(ttl=1)
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

    def getLatestStatus(self, location):
        sqlt = """SELECT status FROM events WHERE location = ? ORDER BY time DESC LIMIT 1;"""
        try:
            status = self.fetch(sqlt,(location,))[0][0]
        except IndexError:
            status = "offline"
        return status
    
    def getLastSeen(self):
        sqlt = """SELECT location, lastseen FROM locations;"""
        lastseen = self.fetch(sqlt)
        ret = {}
        for tup in lastseen:
            try:
                ret[tup[0]] = datetime.strptime(tup[1], "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                ret[tup[0]] = None
        return ret

    def getCal(self, location="1"):
        sqlt = "SELECT calibration FROM calibration WHERE location = ?;"
        return self.fetch(sqlt, (location,))

    def getHist(self, location="1", weekday=0, tzoff=0):
        sqlt = """SELECT 
            cast(strftime('%H',datetime(time, :tzoff || ' hour')) as INT) hour, 
            count(*)/12. perhour 
            FROM events 
            WHERE time > datetime('now','-28 day') 
            AND cast(strftime('%w',datetime(time, :tzoff || ' hour')) as INT) = :wkday 
            AND location=:loc
            GROUP BY hour;"""

        d = self.fetch(sqlt, {"tzoff": "-%d" % (tzoff,), "wkday": weekday, "loc": location})

        b = [0 for ix in range(24)]
        for bin, val in d:
            b[bin] = min(val,1)

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
                    WHERE location = ? AND time > 
                    datetime('now', ? || ' hours')) 
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
                    WHERE location = ? AND time > 
                    datetime('now', ? || ' hours')) 
                WHERE cstart > 0 OR cend > 0)
            WHERE cstart > 0
        """
        return self.fetch(sqlt, (location, -hours))

    def getCurrent(self, location="1", minutes=-60):
        return self.fetch(
            """
            SELECT location, current, time 
            FROM rawcurrent 
            WHERE time > datetime(
                (SELECT max(time) FROM rawcurrent), ? || ' minutes'
            ) 
            AND location = ?
            """,
            (-minutes, location),
        )

    def getCurrentRange(self, location="1", start="", end="", pad=10):
        sqlt = """
        SELECT location,current,time
            FROM rawcurrent 
            WHERE time > datetime(:start, '-' || :pad || ' seconds')
            AND time < COALESCE(datetime(:end, '+' || :pad || ' seconds'), datetime('now'))
            AND location = :loc
        """
        return self.fetch(sqlt, {"start": start, "end": end, "loc": location, "pad": pad})
    
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

    @ttl_cache(ttl=1)
    def getDeviceLocation(self,device=""):
        sqlt = """SELECT location FROM devices WHERE device = ?;"""
        try:
            return self.fetch(sqlt,(device,))[0][0]
        except Exception as e:
            print("couldn't get device location: %s" % e)
            return None
        
    def getDeviceCalibration(self,device=""):
        sqlt = """SELECT calibration FROM devices WHERE device = ?;"""
        try:
            return float(self.fetch(sqlt,(device,))[0][0])
        except Exception as e:
            print(e)
            return 1.0

    def setLocationCalibration(self,location=None, cal=1.0):
        sqlt = """UPDATE devices SET calibration = ? WHERE location = ?"""
        try:
            self.insert(sqlt,(cal, location))
        except Exception as e:
            print("failed to set calibration for %s: %s"% (location, e))
            pass
        
    def getLocationCalibration(self,location=None):
        sqlt = """SELECT COALESCE(calibration,1.0) FROM devices 
            JOIN locations ON devices.location = locations.location
            WHERE devices.location = ?"""
        try:
            return float(self.fetch(sqlt, (location,))[0][0])
        except Exception:
            return 1.0

    def getLocationCalibrationPow(self,location=None):
        sqlt = """SELECT COALESCE(cal_pow,1.0) FROM devices 
            JOIN locations ON devices.location = locations.location
            WHERE devices.location = ?"""
        try:
            return float(self.fetch(sqlt, (location,))[0][0])
        except Exception:
            return 1.0
        
    @ttl_cache(ttl=1)
    def checkDevice(self,uuid):
        try:
            return bool(self.fetch("SELECT count(*) > 0 FROM devices WHERE device = ?", (uuid,))[0][0])
        except Exception:
            return False
        
    def inesertDevice(self,uuid=None):
        if (self.checkDevice(uuid) or uuid is None):
            return
        return self.insert("INSERT OR IGNORE INTO devices VALUES (?,null,'5555',null,datetime('now'));", (uuid,))
    

if __name__ == "__main__":
    db = LaundryDb()

    print(db.getWashCycles("4", 48))

    pass
