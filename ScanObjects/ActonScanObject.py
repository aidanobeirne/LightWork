import sys
import os
from ParentClasses.PI_commands import Acton


class ActonScanObject(Acton):
    def __init__(self, scan_values, address ='11', scan_nest_index=0):
        super().__init__(com_number=address)
        self.meta_data = {}
        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = 'acton'
        
    def set_scan_value(self, value):
        self.wavelength_nm = value
	
    def get_save_data(self, value):
        return {'scan wavelength [nm]': value, 'Acton readout wavelength [nm]' : self.wavelength_nm}
	
    def close(self):
        pass
		
		