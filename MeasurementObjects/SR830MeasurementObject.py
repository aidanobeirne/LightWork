import sys
import os
import numpy as np
import time
from ParentClasses import SR830

######## TO DO: Still need to set wait time and other parameters.
    
class SR830MeasurementObject(SR830):
    def __init__(self, port='GPIB0::11::INSTR', TCs_to_wait=9.23, navg=50):
        super().__init__(port=port, read_termination='\r')
        self.scan_instrument_name = 'SR830'
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
        if tmp := TCs_to_wait: self.meta_data['TCs_to_wait'] = tmp #google walrus ooperator if you dont understand
        if tmp := navg: self.meta_data['navg'] = tmp

        
    def close(self):
        pass

