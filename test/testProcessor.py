import unittest
from HeuristicSignalProcessor import State, HeuristicSignalProcessor
from HistogramSignalProcessor import HistogramSignalProcessor
import os

class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.p = HeuristicSignalProcessor(cal=0)    
        self.p = HistogramSignalProcessor()
    

    def test_files(self):
        dir = "data"
        for file in os.listdir(dir):
            print(file)
            state = file.split('_')[0]
            ds = State[state.upper()]
            s = State.NONE
            n = 0
            c = 0
            t = 0

            with open(os.path.join(dir,file)) as f:
                self.p.reset()
                self.p.cal = 1.0
                for line in f:
                    ns = self.p.process_sample(float(line))
                    c += 1
                    if (ns is not None):
                        print("%d: %s (%s)" %(c,ns.name,ds.name))
                        s = ns
                        t += 1
                    if (s == ds):
                        n += 1
            print(n,c)
            self.assertTrue(n > 0.7*c)
            self.assertTrue(t < 3)
