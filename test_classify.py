import sys
from laundaemon import SignalProcessor

if __name__ == "__main__":
    cal = 1.0

    try:
        cal = float(sys.argv[2])
    except Exception:
        cal = 1.0

    proc = SignalProcessor(100, 50, cal)

    with open(sys.argv[1]) as fh:
        for line in fh.readlines():
            status = proc.process_sample(float(line), only_diff=False)

            if status is None:
                continue
            print(status)
