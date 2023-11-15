import socket
import select
import datetime

from collections import namedtuple
from DataMuncher import DataMuncher

UDP_IP = "0.0.0.0"
Input = namedtuple('Input', ['socket','location'])

class SocketMuncher(DataMuncher):
    def sanitize_data(self, data):
        return float(data.strip())
 
    def run(self):
        while True:
            sockets = [i.socket for i in self.inputs]
            readable, _writable, _except = select.select(sockets, [], [], 1)
            now = datetime.datetime.utcnow()
            
            for s in readable:
                data, addr = s.recvfrom(32)
                input = self.inputs[sockets.index(s)]
                loc = input.location

                try:
                    sanitized = self.sanitize_data(data)
                except ValueError:
                    print("bad value %s from %s" % (data, addr))
                    continue
                
                self.process_sample(loc,sanitized,now)

            self.checkOffline(now)

    def __init__(self, base_port):
        DataMuncher.__init__(self)
        self.publish_input = True

        self.inputs = []

        for loc in self.locations:
            port = base_port + int(loc)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((UDP_IP, port))

            self.inputs.append(Input(sock, loc))