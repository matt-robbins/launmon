from pywebpush import webpush, WebPushException
from db import LaundryDb
from multiprocessing import Process
import json
import sys

def push_main(subscription={},data={}):
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(data),
            vapid_private_key="m1Wni8qP-jjDa0jPaczGSZRsulQHAm5olCv7bXO81Go",
            vapid_claims={
                    "sub": "mailto:matthew.robbins@gmail.com",
                })
    except WebPushException as ex:
        print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
        # Mozilla returns additional information in the body of the response.
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                extra.code,
                extra.errno,
                extra.message
                )

def push(db, location, message):
    for s in db.getSubscriptions(location):
        sub = json.loads(s[0])
        name = db.getName(location)

        # note that we don't explicitly wait() for the process to finish
        # tested and I don't *think* this causes zombies. lol.
        p = Process(target=push_main,args=(sub,{"location":name,"message":message, "sass": "Get it!"}))
        p.start()
        #db.deleteSubscription(endpoint=sub['endpoint'],location=location)

if __name__ == '__main__':
    d = LaundryDb()
    location = '1'
    if (len(sys.argv) > 1):
        location = sys.argv[1]

    push(d,location)
