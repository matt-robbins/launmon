from redis import Redis
from db import LaundryDb

class DataSink:
    def process_data(self,location,data,time):
        pass
    def __init__(self):
        pass

class Publisher:
    def publish(channel,data):
        pass
    def __init__(Self):
        pass

class RedisPublisher(Publisher):
    def publish(self,channel,data):
        channel = ':'.join(channel)
        try:
            self.r.publish(channel,data)
        except Exception as e:
            print ("failed to publish data %s" % e)
            pass
    def __init__(self):
        self.r = Redis()

class CurrentSink(DataSink):
    def process_data(self,location,data,time):
        self.publisher.publish([self.channel,location],data)
        self.db.addCurrentReading(
            location, data, time
        )
            
    def __init__(self,channel="current", publisher=RedisPublisher(),db=LaundryDb()):
        self.channel=channel
        self.publisher = publisher
        self.db = db

class StatusSink(DataSink):
    def process_data(self,location,data,time):
        status = data
        try:
            oldstatus = self.db.getLatestStatus(location)
        except Exception as e:
            print("failed to get old status for %s: %s" % (location, e))
            return
        
        if (oldstatus == status):
            return
        
        print("machine %s changed state: %s" % (location, status))
        
        try:
            self.db.addEvent(location, status, time)
        except Exception as e:
            print ("failed to insert event for %s: %s" % (location, e))
            return

        self.publisher.publish([self.channel,location], oldstatus+":"+status)

    def __init__(self,channel="status", publisher=RedisPublisher(), db=LaundryDb()):
        self.channel=channel
        self.publisher = publisher
        self.db = db