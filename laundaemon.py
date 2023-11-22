import asyncio
import aiomqtt
from DataMuncher import DataMuncher
from datetime import datetime
import mqttsecrets as secrets

HOST = "0.0.0.0"
PORT = 5001

class V1Protocol(asyncio.DatagramProtocol):
    def __init__(self, muncher):
        super().__init__()
        self.muncher = muncher

    def connection_made(self, transport):
        self.transport = transport
        try:
            self.port = transport.get_extra_info('socket').getsockname()[1]
        except Exception:
            self.port = None

    def datagram_received(self, data, addr):
        
        # Here is where you would push message to whatever methods/classes you want.
        loc = str(self.port-5000)
        try:
            sample = float(data.decode().strip())
        except Exception:
            return
        self.muncher.process_sample(loc,sample,datetime.utcnow())


class V2Protocol(asyncio.DatagramProtocol):
    def __init__(self, muncher):
        super().__init__()
        self.muncher = muncher

    def connection_made(self, transport):
        self.transport = transport
        
    def datagram_received(self, data, addr):
        # Here is where you would push message to whatever methods/classes you want.
        print(f"Received Syslog message: {data} at {self.port}")


async def mqtt_main(muncher):
    while True:
        try:
            async with aiomqtt.Client(secrets.HOST,username=secrets.USER,password=secrets.PASS) as client:
                async with client.messages() as messages:
                    await client.subscribe("+/sensor/current/state")
                    async for msg in messages:
                        try:
                            sample = float(msg.payload.decode())
                        except ValueError:
                            print("bad message %s" % msg.payload)
                            return
                        device = msg.topic.value.split("/")[0].split('-')[-1]
                        loc = muncher.get_device_location(device)
                        if (loc is None):
                            loc = device

                        muncher.process_sample(loc,sample,datetime.utcnow())

        except Exception as e:
            print("yoopsy: %s" % e)
            await asyncio.sleep(1)

async def checker(muncher):
    while True:
        muncher.checkOffline(datetime.utcnow())
        await asyncio.sleep(1)


if __name__ == '__main__':
    m = DataMuncher()
    loop = asyncio.get_event_loop()
    for p in range(1,5):
        t = loop.create_datagram_endpoint(lambda: V1Protocol(m), local_addr=('0.0.0.0', PORT+p))
        loop.run_until_complete(t) # Server starts listening

    # t = loop.create_datagram_endpoint(lambda: V2Protocol(m), local_addr=('0.0.0.0', 5555))
    # loop.run_until_complete(t)

    loop.create_task(mqtt_main(m))
    loop.create_task(checker(m))
    loop.run_forever()