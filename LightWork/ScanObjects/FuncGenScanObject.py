import time
import numpy as np
import sys
import os
from LightWork.ParentClasses import textronix_func_gen as tfg


class FuncGenScanObject():
    """THIS SCANOBJECT NEEDS TO BE REWORKED: currently changes the offset of both channels together (i.e. one can only use this to run 
    doping sweeps where V_TG = V_BG.)
    """
    def __init__(self, 
        scan_values,
        scan_nest_index,
        name='fg',
        visa_address='USB0::0x0699::0x0353::2147069::INSTR'):

        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = name
        self.visa_address = visa_address
        with tfg.FuncGen(self.visa_address, verbose=False) as fgen:
            self.meta_data = fgen.get_settings_with_phase()
        
    def set_scan_value(self, value):
        with tfg.FuncGen(self.visa_address, verbose=False) as fgen:
            fgen.ch1.set_offset(value)
            fgen.ch2.set_offset(value)

    def get_scan_value(self):
        with tfg.FuncGen(self.visa_address, verbose=False) as fgen:
            offone = fgen.ch1.get_offset()
            offtwo = fgen.ch2.get_offset()
        dat = {'deg': {'CH1': offone, 'CH2': offtwo}}
        return dat
	
    def get_save_data(self, value=None):
        pass
	
    def close(self):
        pass
		
		