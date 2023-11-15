
from datetime import datetime, timedelta
import db
from redis import Redis
from HeuristicSignalProcessor import HeuristicSignalProcessor

OFFLINE_THRESHOLD_S = 10

class DataMuncher:
    def publish(self, channel, data):
        try:
            self.r.publish(channel,data)
        except:
            print ("failed to publish data")
            pass

    def setstatus(self, location, status, time):
        oldstatus = self.db.getLatestStatus(location)
        if (oldstatus == status):
            return
        
        print("machine %s changed state: %s" % (location, status))
        
        self.db.addEvent(location, status, time)
        self.publish("status:"+location, oldstatus+":"+status)

    def checkOffline(self,time):
        for l in self.locations:
            if (self.online[l] and time - self.lastseen[l] > timedelta(seconds=OFFLINE_THRESHOLD_S)):
                self.online[l] = False
                self.processors[l].reset()
                self.setstatus(l,"offline", time)

    def process_sample(self, location, data, time):

        only_diff =  self.online[location]

        self.online[location] = True
        self.lastseen[location] = time

        if (self.publish_input):
            self.publish("current:"+location,data)
            self.db.addCurrentReading(
                location, data, time
            )

        cal = self.db.getLocationCalibration(location)
        status = self.processors[location].process_sample(data*cal, only_diff=only_diff)
        if status is None:
            return

        self.setstatus(location, status.name.lower(), time)


    def run(self):
        pass

    def __init__(self):
        self.db = db.LaundryDb()
        self.r = Redis()

        self.locations = self.db.getLocations()
        self.publish_input = False

        self.online = {}
        self.lastseen = {}
        self.processors = {}
        now = datetime.utcnow()
        for l in self.locations:
            self.processors[l] = HeuristicSignalProcessor()
            self.lastseen[l] = now
            self.online[l] = False        

