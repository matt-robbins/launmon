import socket
import select
import datetime
from DataMuncher import DataMuncher
import asyncio
from concurrent.futures import ThreadPoolExecutor

UDP_IP = "0.0.0.0"
UDP_CAPTURE_PORT=5555
PACKET_MAXLEN=24

class SocketMuncherV2(DataMuncher):
    def sanitize_data(self, data):
        uuid,current = data.split()
        return [uuid.strip().decode('ascii'),float(current.strip())]
    
    def run(self):
        while True:
            readable, _writable, _except = select.select([self.sock], [], [], 1)
            for s in readable:
                data = s.recvfrom(PACKET_MAXLEN)[0]
                now = datetime.datetime.utcnow()
                try:
                    uuid,sample = self.sanitize_data(data)
                except Exception as e:
                    print("Failed to parse incoming data packet: '%s': %s"%(data,e))
                    continue
                
                location = self.db.getDeviceLocation(uuid)
                if (location is None):
                    print("couldn't find location for device '%s'"%uuid)
                    continue

                self.process_sample(location,sample,now)
            
    def __init__(self, addr=UDP_IP, port=UDP_CAPTURE_PORT):
        DataMuncher.__init__(self)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((addr,port))


if __name__ == "__main__":

    m = SocketMuncherV2(UDP_IP,5555)
    m2 = SocketMuncherV2(UDP_IP, 5556)

    executor = ThreadPoolExecutor(2)
    loop = asyncio.new_event_loop()
    loop.run_in_executor(executor, m.run)
    loop.run_in_executor(executor, m2.run)
    loop.run_forever()
