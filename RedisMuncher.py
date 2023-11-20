
from datetime import datetime
from redis import Redis
from DataMuncher import DataMuncher

class RedisMuncher(DataMuncher):
    
    def run(self):
        while True:
            message = self.p.get_message(timeout=1)
            if (message is not None):
                location = str.split(message['channel'].decode(),':')[1]
                sample = float(message['data'].decode().strip())
                self.process_sample(location,sample, datetime.utcnow())
            
    def __init__(self,master=True):
        DataMuncher.__init__(self)
        self.input = Redis()
        self.master = True
        self.p = self.input.pubsub(ignore_subscribe_messages=True)
        self.p.psubscribe("current:*")
        
if __name__ == "__main__":
    w = RedisMuncher()
    w.run()
