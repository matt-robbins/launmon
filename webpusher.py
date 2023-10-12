#!/usr/bin/env python
import redis
import json
import asyncio
import db
from webpush import push_main
import concurrent.futures

class Webpusher:
    def __init__(self,db):
        self.redis = redis.Redis()
        self.p = self.redis.pubsub(ignore_subscribe_messages=True)
        self.p.psubscribe("status:*")
        self.db = db

    def run(self):
        for msg in self.p.listen():

            _, location = str.split(msg['channel'].decode(),':')
            trans = msg['data'].decode()

            event_text = ""
            sass = "Get it!"
            if (trans in ["none:wash", "dry:both"]):
                event_text = "Washer Started"
                sass = "Woohoo!"
            elif (trans in ["none:dry","wash:both"]):
                event_text = "Dryer Started"
                sass = "Okay!"
            elif (trans in ["both:wash","dry:none"]):
                event_text = "Dryer Done"
                sass = "Get it while it's hot!"
            elif (trans in ["both:dry","wash:none"]):
                event_text = "Washer Done"
                sass = "Squeaky Clean!"
            elif (trans == "both:none"):
                event_text = "Done"

            payload = {"location":"","message":event_text, "sass":sass}

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for s in db.getSubscriptions(location):
                    sub = json.loads(s[0])
                    name = db.getName(location)
                    payload['location'] = name

                    futures.append(executor.submit(push_main,sub,payload))
                for f in futures:
                    try:
                        res = f.result()
                        print(res)
                    except Exception:
                        print(sub['endpoint'])
                        db.deleteSubscription(sub['endpoint'],location)
 
        
if __name__ == "__main__":
    db = db.LaundryDb()
    w = Webpusher(db)
    w.run()