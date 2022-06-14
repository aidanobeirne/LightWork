import time
import numpy as np
import sys
import os
from pymeasure.adapters import VISAAdapter
from LightWork.ParentClasses import Keithley2400


class KeithleyScanObject(Keithley2400):
    def __init__(self, scan_values, address ='16', name='TG', compliance_current=300e-9, scan_nest_index=0):
        """
        
        Parameters
        ----------
        scan_values : LIST OR ARRAY
            VOLTAGE VALUES TO SCAN KEITHLEY OVER.
        address : STR, optional
            COM ADDRESS. The default is '16'.
        name : STR, optional
            UNIQUE NAME FOR THIS KEITHLEY IN PARTICULAR (USEFUL WHEN RUNNING SCANS WITH MULTIPLE KEITHLEYS). The default is 'TG'.
        compliance_current : FLOAT, optional
            COMPLIANCE CURRENT OF THE KEITHLEY IN AMPS. The default is 300e-9.
        scan_nest_index : INT, optional
            THE INDEX OF THIS INSTRUMENT IN THE SCAN PROCEDURE. 0 CORRESPONDS TO AN INSTRUMENT WHOSE VALUES ARE CHANGED ONLY ONCE, 1 CORRESPONDS
            TO AN INSTRUMENT WHOSE VALUES ARE CHANGED TWICE, ETC. The default is 0.

        Returns
        -------
        None.

        """
        super().__init__(VISAAdapter('ASRL{}::INSTR'.format(address), read_termination='\r'))
        self.meta_data = {}
        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = 'keithley_{}'.format(name)
        self.compliance_current = compliance_current
        self.source_enabled = 1
        self.enable_source()
        
    def set_scan_value(self, value):
        self.ramp_to_voltage_step_size(value, step_size = 0.01, pause = 0.01)
	
    def get_save_data(self, value=None):
        currents = []
        for i in range(30):
            # not sure which current reading to use. jenny had problems with the mean current reading, which averages all values in the buffer
            # currents.append(self.mean_current)
            currents.append(self.current[1])
            time.sleep(0.01)
        data = {'voltage [V]' : value, 'leakage current [nA]' : 1e-9*np.mean(currents)}
        print('{}, {} V, {} nA leakage current'.format(self.scan_instrument_name, value, np.round(1e-9*np.mean(currents), 4)))
        return data
	
    def close(self):
        self.ramp_to_voltage_step_size(0, step_size = 0.01, pause = 0.01)
		
		