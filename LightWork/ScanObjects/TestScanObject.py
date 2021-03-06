import time
import numpy as np
import random
import sys
import os


class TestScanObject():
    def __init__(self, scan_values, name='Test scan instrument', scan_nest_index=0):
        """
        
        Parameters
        ----------
        scan_values : LIST OR ARRAY
            VOLTAGE VALUES TO SCAN KEITHLEY OVER.
        name : STR, optional
            UNIQUE NAME FOR THIS 
        scan_nest_index : INT, optional
            THE INDEX OF THIS INSTRUMENT IN THE SCAN PROCEDURE. 0 CORRESPONDS TO AN INSTRUMENT WHOSE VALUES ARE CHANGED ONLY ONCE, 1 CORRESPONDS
            TO AN INSTRUMENT WHOSE VALUES ARE CHANGED TWICE, ETC. The default is 0.

        Returns
        -------
        None.

        """
        
        self.meta_data = {'some parameter': 0.1}
        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = name
        
    def set_scan_value(self, value):
        print()
        print('{} set to {}'.format(self.scan_instrument_name, value))
	
    def get_save_data(self, value):
        return {'dat1':value, 'dat2':10}

    def get_scan_value(self):
        return 'Test units', random.uniform(0,1)

    def close(self):
        pass