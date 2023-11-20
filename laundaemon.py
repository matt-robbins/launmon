
import sys
from DataMuncher import DataMuncher
from SocketMuncher import SocketMuncher
from SocketMuncherV2 import SocketMuncherV2
from RedisMuncher import RedisMuncher
from MqttMuncher import MqttMuncher
from multiprocessing import Process
import time
from datetime import datetime

class OfflineChecker(DataMuncher):
    def run(self,):
        while True:
            self.checkOffline(datetime.utcnow())
            time.sleep(1)

if __name__ == "__main__":
    base_port = 5000
    if len(sys.argv) > 2:
        base_port = int(sys.argv[2])

    munchers = [
        SocketMuncher(base_port),
        SocketMuncherV2(),
        MqttMuncher(host="375lincoln.nyc",username="launmon",password="monny"),
        OfflineChecker(),
        RedisMuncher(master=True)
    ]
    processes = []
    for m in munchers:
        p = Process(target=m.run)
        processes.append(p)
        p.start()
