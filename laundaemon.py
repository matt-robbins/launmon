import getstatus as gs
import numpy as np
import socket
import select
import datetime
import os
import sys
import db
import webpush
from HeuristicSignalProcessor import HeuristicSignalProcessor
from HistogramSignalProcessor import HistogramSignalProcessor

UDP_IP = "0.0.0.0"

STATUS_PATH = "/tmp/laundrystatus"

class SocketReader:
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

                self.db.addCurrentReading(
                    machine, sanitized, datetime.datetime.utcnow()
                )
                status = self.processors[ix].process_sample(sanitized)

                if status is None:
                    continue

                print("machine %s changed state: %s" % (machine, status))
                self.setstatus(machine, status.name.lower())

    def setstatus(self, machine, status):
        try:
            os.symlink(STATUS_PATH + "/" + status, STATUS_PATH + "/tmp")
            os.rename(STATUS_PATH + "/tmp", STATUS_PATH + "/" + machine)
        except FileExistsError:
            pass
        self.db.addEvent(machine, status, datetime.datetime.utcnow())

        if status == "none":
            webpush.push(self.db,machine)
            
    def __init__(self, nlocations, base_port):
        try:
            os.mkdir(STATUS_PATH)
        except FileExistsError:
            pass

        for st in ["none", "wash", "dry", "both"]:
            with open(STATUS_PATH + "/" + st, "w") as f:
                f.write(st)

        cals = []
        try:
            with open("calibration.txt", "r") as f:
                for line in f.readlines():
                    cals.append(float(line))
        except FileNotFoundError:
            print("no calibration file -- setting all factors to 1.0")
            cals = [1.0, 1.0, 1.0, 1.0]

        self.db = db.LaundryDb()

        self.sockets = []
        self.processors = []
        self.ports = []
        self.machines = []
        for i in range(nlocations):
            port = base_port + 1 + i
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((UDP_IP, port))
            self.ports.append(port)
            self.sockets.append(sock)
            self.processors.append(HeuristicSignalProcessor(cal=cals[i]))
            self.machines.append(str(i + 1))


if __name__ == "__main__":
    base_port = 5000
    if len(sys.argv) > 2:
        base_port = int(sys.argv[2])

    w = SocketReader(4, base_port)
    w.run()
