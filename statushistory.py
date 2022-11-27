import getstatus as gs
from collections import deque
import numpy as np

def statushistory(file="data/current.txt"):


    with open(file) as f:
        lines = f.readlines()
        n = len(lines)-1
        dq = deque(lines[1:100])
        m = 0

        for i in range(101,n):
            ts = dq[0].split()[0]
            x = np.array([float(l.split()[1]) for l in dq])
            hs = gs.hist(x)

            w_s = gs.compare(gs.file2hist('data/wash'),hs)
            d_s = gs.compare(gs.file2hist('data/dry'),hs)
            b_s = gs.compare(gs.file2hist('data/both'),hs)

            dq.popleft()
            dq.append(lines[i])

            newm = np.argmax(np.array([w_s,d_s,b_s]))
            if (np.argmax(hs) < 3):
                newm = -1  
            m = newm
            print(m)
    
    return 0



if __name__ == "__main__":
    statushistory()
    pass

