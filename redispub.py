import socket
import select
import redis
import sys

UDP_IP = "0.0.0.0"

class RedisPub:
    def sanitize_data(self, data):
        return float(data.strip())
    
    def run(self):
        while True:
            readable, _writable, _except = select.select(self.sockets, [], [])
            for s in readable:
                data, addr = s.recvfrom(1024)
                port = s.getsockname()[1]
                ix = self.ports.index(port)
                try:
                    sanitized = self.sanitize_data(data)
                except ValueError:
                    print("bad value %s from %s" % (data, addr))
                    continue
                machine = self.machines[ix]
                self.r.publish("laundry:"+machine,sanitized)

    def __init__(self, nlocations, base_port):
        self.r = redis.Redis(host="375lincoln.nyc",password="skinnytires")
        self.sockets = []
        self.ports = []
        self.machines = []
        for i in range(nlocations):
            port = base_port + 1 + i
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((UDP_IP, port))
            self.ports.append(port)
            self.sockets.append(sock)
            self.machines.append(str(i + 1))

if __name__ == "__main__":
    port = 3000
    if (len(sys.argv) > 2):
        port = int(sys.argv[2])
        
    r = RedisPub(4,port)
    r.run()
