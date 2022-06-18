import sys
import os
import random
import time


class TestMeasurementObject():
    def __init__(self, name='Test measurement instrument', wait_time_in_s=0.1):
        self.meta_data = {'some measurement parameter':-8}
        self.scan_instrument_name = name
        self.wait_time_in_s = 0.1
            
    def measure(self):
        data = []
        data.append(random.uniform(0,1))
        time.sleep(self.wait_time_in_s)
        return data
        
    def close(self):
        pass