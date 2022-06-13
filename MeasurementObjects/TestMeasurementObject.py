import sys
import os
import random


class TestMeasurementObject():
    def __init__(self):
        self.meta_data = {'some measurement parameter':-8}
        self.scan_instrument_name = 'Test Measurement Object'
            
    def measure(self):
        data = []
        data.append(random.uniform(0,1))
        return data
        
    def close(self):
        pass