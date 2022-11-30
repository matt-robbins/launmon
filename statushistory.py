import getstatus as gs
from collections import deque
import numpy as np
import socket
import functools
import os
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

STATUS_PATH = '/tmp/laundrystatus'
old_status = ''

@functools.cache
def get_training_histograms():
    files = os.listdir("data")
    ret = []
    for f in files:
        label = f.split('_')[0]
        ret.append({'hist': gs.file2hist('data/%s' % f),'label':label})

    return ret

def buffer_classify(buf):
    hs = gs.hist(buf)
    model = get_training_histograms()

    scores = [gs.compare(m["hist"], hs) for m in model]
    maxix = np.argmax(np.array(scores))
    label = [m["label"] for m in model][maxix]

    return label

def watch_status(machine_name,port=5005):
    N = 100; oN = 50
    x = np.zeros((N,1))
    ix = 0
    oix = -1
    STATE = 0

    get_training_histograms()

    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, port))
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        try:
            x[ix]=float(data.split()[1])
        except Exception as e:
            print(data)
            continue
        ix = ix + 1 if (ix < N-1) else 0
        oix = oix + 1 if (oix < oN-1) else 0
        if (oix != 0):
            continue

        setstatus(machine_name,buffer_classify(x))

def setstatus(machine,status):
    print(status)
    global old_status
    if (status!=old_status):
        print('state changed from %s to %s' %(old_status,status))

        pass # todo hook in some kind of notification
    try:
        os.symlink(STATUS_PATH+'/'+status,STATUS_PATH+'/'+machine)
    except FileExistsError as e:
        pass
    old_status=status

if __name__ == "__main__":
    
    try:
        os.mkdir(STATUS_PATH)
    except FileExistsError as e:
        pass

    for st in ['none','wash','dry','both']:
        with open(STATUS_PATH+'/'+st,'w') as f:
            f.write(st)

    floor = 0

    if (len(sys.argv) > 1):
        floor = sys.argv[1]
    
    port = 5000+int(floor)
    if (len(sys.argv) > 2):
        port = int(sys.argv[2])

    print(floor)
    print(port)

    watch_status(floor,port)

