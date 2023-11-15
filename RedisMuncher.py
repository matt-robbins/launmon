
import datetime
from redis import Redis
from DataMuncher import DataMuncher

class RedisMuncher(DataMuncher):
    
    def run(self):
        self.p.psubscribe("current:*")

        while True:
            message = self.p.get_message(timeout=1)
            now = datetime.datetime.utcnow()

            if (message is not None):
                location = str.split(message['channel'].decode(),':')[1]
                sample = float(message['data'].decode().strip())
                
                self.process_sample(location, sample, now)

            self.checkOffline(now)
            
    def __init__(self):
        DataMuncher.__init__(self)
        self.input = Redis()

        self.p = self.input.pubsub(ignore_subscribe_messages=True)
        
if __name__ == "__main__":
    w = RedisMuncher()
    w.run()
