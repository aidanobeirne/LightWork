import sys
import os
import numpy as np
import time
from LightWork.ParentClasses import SR830

# Time Constant settings are coded as follows:
# 0 : 10e-6,  1 : 30e-6,   2 : 100e-6,  3 : 300e-6,  4 : 1e-3,  5 : 3e-3,
# 6 : 10e-3,  7 : 30e-3,   8 : 100e-3,  9 : 300e-3, 10: 1,       11: 3, 
# 12: 10,    13: 30,    14: 100,    15: 300,  16: 1000,   17: 3000,
#  18: 10000,    19: 30000
#  Sensitivity settings are coded as follows:
# 0 : '2 nV/fA',  1 : '5 nV/fA',  2 : '10 nV/fA',   3 : '20 nV/fA',  4 : '50 nV/fA',
#  5 : '100 nV/fA', 6 : '200 nV/fA', 7 : '500 nV/fA',  8 : '1 uV/pA',  9 : '3 uV/pA',
# 10: '5 uV/pA', 11: '10 uV/pA', 12: '20 uV/pA', 13: '50 uV/pA',  14: '100 uV/pA',
#  15: '200 uV/pA', 16: '500 uV/pA',  17: '1 mV/nA',    18: '2 mV/nA',   19: '5 mV/nA',
#   20: '10 mV/nA', 21: '20 mV/nA', 22: '50 mV/nA', 23: '100 mV/nA', 24: '200 mV/nA',
#  25: '500 mV/nA',   26: '1V/uA'
#
    
class SR830MeasurementObject(SR830):
    def __init__(self, name='SR830', port='GPIB0::11::INSTR', TC=0, sens=0, TCs_to_wait=9.23, navg=50):
        super().__init__(port=port, read_termination='\r')
        self.scan_instrument_name = name
        self.setTC(TC)
        self.setsens(sens)
        self.meta_data = {}
        self.update_meta_data(TCs_to_wait=TCs_to_wait, navg = navg)      
            
    def measure(self):
        time.sleep(self.meta_data['TC'] * self.meta_data['TCs to wait'])
        x_values_to_be_averaged = []
        y_values_to_be_averaged = []
        for i in range(self.meta_data['navg']):
            time.sleep(np.random.uniform(0.01, 0.05))
            x_values_to_be_averaged.append(self.getX())
            time.sleep(0.005)
            y_values_to_be_averaged.append(self.getY())
        X = np.mean(x_values_to_be_averaged)
        Y = np.mean(y_values_to_be_averaged)
        R = np.sqrt(X**2+Y**2)
        Theta = np.arctan(np.true_divide(Y,X))
        data = {'X': X, 'Y': Y, 'R': R, 'Theta': Theta}
        return data
    
    def update_meta_data(self, TCs_to_wait=None, navg=None):
        self.meta_data['TC'] = self.getTC()
        self.meta_data['sensitivity'] = self.getsens()

        # any values that cannot be directly read off the LockIn are updated where the sentinel value is None
        self.meta_data['TCs_to_wait'] = TCs_to_wait if TCs_to_wait is not None else self.meta_data['TCs_to_wait']
        self.meta_data['navg'] = navg if navg is not None else self.meta_data['navg']
        

        
    def close(self):
        pass

