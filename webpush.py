from pywebpush import webpush, WebPushException
from db import LaundryDb
from multiprocessing import Process
import json
import sys

def push(subscription={}):
    try:
        webpush(
            subscription_info=subscription,
            data="Get it while it's hot.",
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

if __name__ == '__main__':
    d = LaundryDb()
    location = '1'
    if (len(sys.argv) > 1):
        location = sys.argv[1]

    for s in d.getSubscriptions(location):
        sub = json.loads(s[0])
        p = Process(target=push,args=(sub,))
        p.start()
        print(sub['endpoint'])
        d.deleteSubscription(endpoint=sub['endpoint'],location=location)

