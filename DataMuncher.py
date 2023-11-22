
from datetime import datetime, timedelta
import db
from redis import Redis
from HeuristicSignalProcessor import HeuristicSignalProcessor
from DataSink import CurrentSink, StatusSink

OFFLINE_THRESHOLD_S = 10

class DataMuncher:

    def checkOffline(self,time=datetime.utcnow()):
        try:
            lastseen = self.db.getLastSeen()
        except Exception as e:
            print("couldn't get status: %s" % e)
            return
        
        for loc in lastseen.keys():
            td = time - lastseen[loc]

            if (td > timedelta(seconds=OFFLINE_THRESHOLD_S)):
                if (self.event_sink):
                    self.event_sink.process_data(loc, "offline", time)

    def get_device_location(self, device):
        try:
            return self.db.getDeviceLocation(device)
        except Exception:
            return None

    def process_sample(self, location, data, time):

        if (self.cur_sink):
            self.cur_sink.process_data(location,data,time)

        if location not in self.locations:
            print("unrecognized location, %s" % location)
            return

        only_diff = (time - self.lastseen[location]).total_seconds() < OFFLINE_THRESHOLD_S
        self.lastseen[location] = time

        try:
            cal = self.db.getLocationCalibration(location)
        except Exception as e:
            print ("failed to get calibration value for %s: %s" % (location, e))
            cal = 1.0

        status = self.processors[location].process_sample(data*cal, only_diff=only_diff)
        if status is None:
            return

        if (self.event_sink):
            self.event_sink.process_data(location, status.name.lower(), time)


    def __init__(self, cur_sink=CurrentSink(),event_sink=StatusSink()):
        self.db = db.LaundryDb()

        self.locations = self.db.getLocations()
        self.cur_sink = cur_sink
        self.event_sink = event_sink

        self.lastseen = {}
        self.processors = {}
        now = datetime.utcnow()
        for loc in self.locations:
            self.processors[loc] = HeuristicSignalProcessor()
            self.lastseen[loc] = now - timedelta(days=1)

