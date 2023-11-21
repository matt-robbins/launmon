
from datetime import datetime, timedelta
import db
from redis import Redis
from HeuristicSignalProcessor import HeuristicSignalProcessor

OFFLINE_THRESHOLD_S = 10

class DataMuncher:
    def publish(self, channel, data):
        try:
            self.r.publish(channel,data)
        except Exception as e:
            print ("failed to publish data %s" % e)
            pass

    def setstatus(self, location, status, time):
        oldstatus = self.db.getLatestStatus(location)
        if (oldstatus == status):
            return
        
        print("machine %s changed state: %s" % (location, status))
        
        self.db.addEvent(location, status, time)
        self.publish("status:"+location, oldstatus+":"+status)

    def checkOffline(self,time=datetime.utcnow()):
        lastseen = self.db.getLastSeen()
        for loc in lastseen.keys():
            if (time - lastseen[loc] > timedelta(seconds=OFFLINE_THRESHOLD_S)):
                self.setstatus(loc,"offline", time)

    def process_sample(self, location, data, time):

        if not self.master:
            self.publish("current:"+location,data)
            self.db.addCurrentReading(
                location, data, time
            )
            return

        if location not in self.locations:
            print("unrecognized location, %s" % location)
            return

        only_diff = (time - self.lastseen[location]).total_seconds() < OFFLINE_THRESHOLD_S
        self.lastseen[location] = time

        cal = self.db.getLocationCalibration(location)
        status = self.processors[location].process_sample(data*cal, only_diff=only_diff)
        if status is None:
            return

        self.setstatus(location, status.name.lower(), time)

    def run(self):
        pass

    def __init__(self, master=False):
        self.db = db.LaundryDb()
        self.r = Redis()

        self.locations = self.db.getLocations()
        self.master = master

        self.lastseen = {}
        self.processors = {}
        now = datetime.utcnow()
        for loc in self.locations:
            self.processors[loc] = HeuristicSignalProcessor()
            self.lastseen[loc] = now - timedelta(days=1)

