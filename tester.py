import socket
import sys


def play_file(f, port):
    # Create a UDP socket at client side

    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    with open(f) as fh:
        for line in fh.readlines():
            sock.sendto(bytes(line, "utf8"), ("127.0.0.1", port))


if __name__ == "__main__":
    port = int(sys.argv[1])
    play_file(sys.argv[2], port)
