import time
import numpy as np
import sys
import os
from ParentClasses import textronix_func_gen


class FuncGenScanObject(FuncGen):
    def __init__(self, 
        scan_values,
        visa_address: str,
        impedance: Tuple[str, str] = ("highZ",) * 2,
        timeout: int = 1000,
        verify_param_set: bool = False,
        override_compatibility: str = "",
        verbose: bool = True,):

        super().__init__(FuncGen('ASRL{}::INSTR'.format(address), read_termination='\r'))
        self.meta_data = {}
        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = 'Function_generator'.format(name)
        
    def set_scan_value(self, value):
        pass
	
    def get_save_data(self, value=None):
        pass
	
    def close(self):
        pass
		
		