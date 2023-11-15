import socket
import select
import datetime
from DataMuncher import DataMuncher

UDP_IP = "0.0.0.0"
UDP_CAPTURE_PORT=5555
PACKET_MAXLEN=24

class SocketMuncherV2(DataMuncher):
    def sanitize_data(self, data):
        uuid,current = data.split()
        return [uuid.strip().decode('ascii'),float(current.strip())]
    
    def run(self):
        while True:
            readable = select.select([self.sock], [], [], 1.0)[0]
            now = datetime.datetime.utcnow()
            for s in readable:
                data=s.recvfrom(PACKET_MAXLEN)[0]
                self.process_packet(data, now)
                try:
                    uuid,sample = self.sanitize_data(data)
                except Exception as e:
                    print("Failed to parse incoming data packet: '%s': %s"%(data,e))
                    continue

                try:
                    self.db.inesertDevice(uuid)
                except Exception as e:
                    print("couldn't insert device %s" % e)
                    continue
                
                location = self.db.getDeviceLocation(uuid)
                if (location is None):
                    print("couldn't find location for device '%s'"%uuid)
                    continue

                self.process_sample(location,sample,now)

            self.checkOffline(now)
            
    def __init__(self):
        DataMuncher.__init__(self)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_CAPTURE_PORT))
        

if __name__ == "__main__":

    r = SocketMuncherV2()
    r.run()
