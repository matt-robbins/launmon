from DataSink import StatusSink
from datetime import datetime
import sys

if __name__ == "__main__":
    loc = ''
    if len(sys.argv) > 1:
        loc = sys.argv[1]
    if len(sys.argv) > 2:
        status = sys.argv[2]

    s = StatusSink()
    s.process_data(loc,status,datetime.utcnow())

