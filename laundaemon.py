import getstatus as gs
import numpy as np
import socket
import select
import datetime
from functools import lru_cache
import os
import sys
import db
from multiprocessing import Process
import webpush
import json

UDP_IP = "0.0.0.0"

STATUS_PATH = "/tmp/laundrystatus"


class SignalProcessor:
    def __init__(self, N, oN, cal=1.0):
        self.N = N
        self.oN = oN
        self.cal = cal
        self.x = np.zeros((N, 1))
        self.ix = 0
        self.oix = -1
        self.state = "none"
        self.old_state = "???"

    def process_sample(self, sample, only_diff=True):
        self.x[self.ix] = sample * self.cal
        # circular buffer index update
        self.ix = self.ix + 1 if (self.ix < self.N - 1) else 0
        self.oix = self.oix + 1 if (self.oix < self.oN - 1) else 0
        if self.oix != 0:
            return None

        self.state = self.buffer_classify(self.x)
        if only_diff and (self.state == self.old_state):
            return None

        if self.old_state == "???":
            self.old_state = self.state
            return None

        self.old_state = self.state

        return self.state

    @lru_cache
    def get_training_histograms(self):
        files = os.listdir("data")
        ret = []
        for f in files:
            label = f.split("_")[0]
            ret.append({"hist": gs.file2hist("data/%s" % f), "label": label})

        return ret

    def buffer_classify(self, buf):
        hs = gs.hist(buf)
        model = self.get_training_histograms()

        scores = [gs.compare(m["hist"], hs) for m in model]
        maxix = np.argmax(np.array(scores))
        label = [m["label"] for m in model][maxix]

        return label


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
                self.setstatus(machine, status)

    def setstatus(self, machine, status):
        try:
            os.symlink(STATUS_PATH + "/" + status, STATUS_PATH + "/tmp")
            os.rename(STATUS_PATH + "/tmp", STATUS_PATH + "/" + machine)
        except FileExistsError:
            pass
        self.db.addEvent(machine, status, datetime.datetime.utcnow())

        if status == "none":
            subs = self.db.getSubscriptions(machine)
            for s in subs:
                sub = json.loads(s[0])
                p = Process(target=webpush.push, args=(sub,))
                p.start()
                # note that we don't explicitly wait() for the process to finish
                # tested and I don't *think* this causes zombies. lol.
                self.db.deleteSubscription(endpoint=sub['endpoint'],location=machine)
            
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
            self.processors.append(SignalProcessor(100, 50, cals[i]))
            self.machines.append(str(i + 1))


if __name__ == "__main__":
    base_port = 5000
    if len(sys.argv) > 2:
        base_port = int(sys.argv[2])

    w = SocketReader(4, base_port)
    w.run()
