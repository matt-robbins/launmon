import unittest
import DataProcessor
from DataProcessor import State, HeuristicSignalProcessor
import os

class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.p = HeuristicSignalProcessor(cal=0)        
    

    def test_files(self):
        dir = "data"
        for file in os.listdir(dir):
            print(file)
            state = file.split('_')[0]
            ds = State[state.upper()]
            s = State(0)
            n = 0
            c = 0
            t = 0

            with open(os.path.join(dir,file)) as f:
                self.p.reset()
                self.p.cal = 1.1
                for line in f:
                    ns = self.p.process_sample(float(line))
                    c += 1
                    if (ns is not None):
                        s = ns
                        t += 1
                    if (s == ds):
                        n += 1
            
            self.assertTrue(n > 0.90*c)
            self.assertTrue(t < 4)
