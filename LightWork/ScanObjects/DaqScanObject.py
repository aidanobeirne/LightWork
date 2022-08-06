import sys
import os
import nidaqmx as daq


class DaqScanObject():
    def __init__(self, scan_values, chan='Dev1/ao0', name='x daq', scan_nest_index=0):
        """
        Parameters
        ----------
        scan_values : LIST OR ARRAY
            ANGLES TO SCAN CAGE ROTATOR OVER. 
        chan : STR, optional
            VOLTAGE CHANNEL . The default is 'Dev1/ao0'.
        name : STR, optional
            UNIQUE NAME. The default is 'x daq'.
        scan_nest_index : INT, optional
           THE INDEX OF THIS INSTRUMENT IN THE scan PROCEDURE. 0 CORRESPONDS TO AN INSTRUMENT WHOSE VALUES ARE CHANGED ONLY ONCE, 1 CORRESPONDS
           TO AN INSTRUMENT WHOSE VALUES ARE CHANGED TWICE, ETC. The default is 0.

        Returns
        -------
        None.

        """
        self.meta_data = {'name':name}
        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = name
        self.daq = daq.Task()
        self.daq.ao_channels.add_ao_voltage_chan(b'{}'.format(chan))
        
    def set_scan_value(self, value):
        self.daq.write(value)

    def get_scan_value(self):
        return 'voltage', 'fix this' #self.daq.read()[0]
	
    def get_save_data(self, value):
        return {'voltage': value}
	
    def close(self):
        pass

		
		