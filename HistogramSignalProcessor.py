
from functools import lru_cache
import os
import numpy as np
import getstatus as gs
from SignalProcessor import SignalProcessor, State
import sys

class HistogramSignalProcessor(SignalProcessor):
    def __init__(self, N=100, oN=50, cal=1.0):
        self.N = N
        self.oN = oN
        self.cal = cal
        self.x = np.zeros((N, 1))
        self.ix = 0
        self.oix = -1
        self.state = State.NONE
        self.old_state = State.NONE

    def reset(self):
        self.x = np.zeros((self.N,1))
        self.ix = 0
        self.oix = -1
        SignalProcessor.reset(self)

    def process_sample(self, sample, only_diff=True):
        self.x[self.ix] = sample * self.cal
        # circular buffer index update
        self.ix = self.ix + 1 if (self.ix < self.N - 1) else 0
        self.oix = self.oix + 1 if (self.oix < self.oN - 1) else 0
        if self.oix != 0:
            return None

        self.state = State[self.buffer_classify(self.x)]
        if only_diff and (self.state == self.old_state):
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

        return label.upper()
    
if __name__ == "__main__":
    p = HistogramSignalProcessor()
    p.cal = 1
    lc = 0
    for line in sys.stdin:

        ns = p.process_sample(float(line))
        lc += 1
        if (ns is not None):
            print("%d: %d" % (lc,ns.value))
