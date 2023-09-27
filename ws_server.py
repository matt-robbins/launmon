#!/usr/bin/env python
import asyncio
import datetime
import random
import websockets
import redis
import json


CONNECTIONS = set()
r = redis.Redis()
p = r.pubsub(ignore_subscribe_messages=True)

async def register(websocket):
    CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTIONS.remove(websocket)

async def show_time():
    while True:
        message = p.get_message()
        if (message is not None):
            print(message)
            ch, machine = str.split(message['channel'].decode(),':')
            data = message['data'].decode()
            packet = {"location": machine, ch: data}

            websockets.broadcast(CONNECTIONS, json.dumps(packet))
        await asyncio.sleep(0.1)

async def main():
    async with websockets.serve(register, "localhost", 5678):
        await show_time()

if __name__ == "__main__":
    p.psubscribe("status:*","current:*")
    asyncio.run(main())