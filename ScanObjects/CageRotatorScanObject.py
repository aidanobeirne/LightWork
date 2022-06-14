import sys
import os
from LightWork.ParentClasses.ThorlabsStages.ThorlabsStages import ThorlabsCageRotator


class CageRotatorScanObject(ThorlabsCageRotator):
    def __init__(self, scan_values, SN_motor='55164244', name='analyzer', scan_nest_index=0):
        """
    
        Parameters
        ----------
        scan_values : LIST OR ARRAY
            ANGLES TO SCAN CAGE ROTATOR OVER. 
        SN_motor : STR, optional
            SERIAL NUMBER OF THE THORLABS CAGE ROTATOR. The default is '55164244'.
        name : STR, optional
            UNIQUE NAME FOR THIS CAGE ROTATOR. The default is 'analyzer'.
        scan_nest_index : INT, optional
           THE INDEX OF THIS INSTRUMENT IN THE scan PROCEDURE. 0 CORRESPONDS TO AN INSTRUMENT WHOSE VALUES ARE CHANGED ONLY ONCE, 1 CORRESPONDS
           TO AN INSTRUMENT WHOSE VALUES ARE CHANGED TWICE, ETC. The default is 0.

        Returns
        -------
        None.

        """
        super().__init__(SN_motor=SN_motor)
        self.meta_data = {'name':name}
        self.scan_values = list(scan_values)
        self.scan_nest_index=scan_nest_index
        self.scan_instrument_name = 'CageRotator_{}'.format(name)
        
    def set_scan_value(self, value):
        self.moveToDeg(value)
	
    def get_save_data(self, value):
        return {'angle [degrees]: value'}
	
    def close(self):
        pass
#        self.close()
		
		