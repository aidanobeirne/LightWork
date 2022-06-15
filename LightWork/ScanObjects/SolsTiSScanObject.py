import sys
import os
from LightWork.ParentClasses.solstis import SolstisError, Solstis
import socket 


class SolsTiSScanObject(Solstis):
    def __init__(self, scan_values, address='192.168.1.222', port=39900, scan_nest_index=0, wavemeter=True):
        super().__init__(address=address, port=port)
        self.meta_data = {}
        self.scan_values = list(scan_values)
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = 'SolsTiS'
        self.wavemeter = wavemeter
        
    def set_scan_value(self, value):
        if self.wavemeter:
            try:
                self.wavemeter_wl = self.set_wave_m_f_r(value)
                if self.wavemeter_wl == 0:
                    self.wavemeter_wl = self.set_wave_m_f_r(value)
            except socket.timeout:
                print('SolsTiS timeout')
                self.etalon_lock(False)
                self.stop_wave_m()
                try:
                    self.wavemeter_wl = self.poll_wave_m()
                except SolstisError:
                    self.wavemeter_wl = value
        else:
            self.move_wave_t(value)
            self.wavemeter_wl = 0
	
    def get_save_data(self, value):
        data = {'scan wavelength [nm]': value , 'wavemeter wavelength [nm]' : self.wavemeter_wl}
        return data
	
    def close(self):
        pass
		
		