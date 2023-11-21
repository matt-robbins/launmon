from datetime import datetime, timedelta
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
        self.publisher.publish([self.channel],data)
        self.db.addCurrentReading(
            location, data, time
        )
            
    def __init__(self,channel="current", publisher=RedisPublisher()):
        self.channel=channel
        self.publisher = publisher
        self.db = LaundryDb()
