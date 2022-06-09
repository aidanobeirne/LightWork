# =============================================================================
# Not sure how to deal with the signal_handler function, so for now I will not inherit the Andor class, but just write a wrapper around it 
# =============================================================================
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname( __file__ )))




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