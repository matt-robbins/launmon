from SignalProcessor import State, SignalProcessor
import sys

# "Expert System" classifier for laundry status given current.
class HeuristicSignalProcessor(SignalProcessor):
    def __init__(self, 
        spike_max=200, wash_th=60, dry_th=700, idle_time=16,both_idle_time=30,cal=1.0):
        self.spike_max = spike_max
        self.wash_th = wash_th
        self.dry_th = dry_th
        self.null_count = 0
        self.idle_time = idle_time
        self.both_idle_time = both_idle_time
        self.both_idle_count = 0
        self.dry_min = 0
        self.cal = cal
        self.spike_count = 0
        self.spike_start = -1
        self.prev_sample = 0
        self.state = State.NONE

    def reset(self):
        self.__init__()

    def process_sample(self, sample, only_diff=True):
        spike = 0

        if (sample > self.prev_sample):
            if (self.spike_start == 0):
                self.spike_count = 0
                self.spike_start = self.prev_sample
            self.spike_count += 1
        elif (self.spike_start != 0):
            spike = self.prev_sample - self.spike_start
            self.spike_start = 0

        self.prev_sample = sample

        new_state = self.state
        diff = sample - self.prev_sample

        # keep track of how long we've been under the wash threshold
        self.null_count = self.null_count + 1 if sample < self.wash_th else 0

        if (self.state == State.NONE): # NONE
            if (spike > self.dry_th):
                new_state = State.DRY
            elif (spike > self.wash_th):
                new_state = State.WASH
    
        elif (self.state == State.WASH): # WASH
            if (spike > self.dry_th and self.spike_count <= 3):
                new_state = State.BOTH
            if (diff > self.dry_th):
                print("setting state to BOTH because of big diff")
                new_state = State.BOTH

        elif (self.state == State.DRY): # DRY
                
            self.dry_time += 1
            if sample < self.dry_th:
                new_state = State.NONE
            elif sample < self.dry_min:
                self.dry_min = sample
            elif spike > self.wash_th and spike < self.spike_max and self.dry_time > 10:
                new_state = State.BOTH
            
        elif (self.state == State.BOTH): # BOTH                

            if (sample < (self.dry_min + self.wash_th)):
                self.both_idle_count += 1
            else:
                self.both_idle_count = 0

            if (self.both_idle_count > self.both_idle_time):
                new_state = State.DRY

            if (sample < self.wash_th):
                new_state = State.NONE
            elif (sample < self.dry_th):
                new_state = State.WASH
            elif (sample < self.dry_min):
                self.dry_min = sample
           
                
        # regardless of current state, reset to null if we time out on low current
        if (self.null_count >= self.idle_time and self.state != 0):
            new_state = State.NONE

        if new_state != self.state:
            self.state = new_state
            if (new_state) == State.DRY:
                self.dry_time = 0
                self.dry_min = sample
            if (new_state == State.BOTH):
                self.both_idle_count = 0
            return new_state
        
        return None

if __name__ == "__main__":
    p = HeuristicSignalProcessor()
    p.cal = 1
    lc = 0
    for line in sys.stdin:

        ns = p.process_sample(float(line))
        lc += 1
        if (ns is not None):
            print("%d: %d" % (lc,ns.value))