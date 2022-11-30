import socket
import sys

def play_file(f):
    # Create a UDP socket at client side

    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    with open(f) as fh:
        for l in fh.readlines():
            sock.sendto(bytes("ts %s" % l,'utf8'), ("127.0.0.1", 5004))

if __name__ == "__main__":
    play_file(sys.argv[1])
