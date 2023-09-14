import socket
UDP_IP = "0.0.0.0"

class RedisPub:
    def __init__(self, nlocations, base_port):
        
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