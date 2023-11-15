
import sys
from SocketMuncher import SocketMuncher

if __name__ == "__main__":
    base_port = 5000
    if len(sys.argv) > 2:
        base_port = int(sys.argv[2])

    w = SocketMuncher(base_port)
    w.run()
