
from LightWork.ParentClasses.HJY import synapseEM_barebones, ihr320
import numpy as np


class ihr320SynapseEMMeasurementObject():
    def __init__(self, name='ihr320_synapseEM', exposure_in_s=1, grating=1, numavgs=1, center_wl=700, ystart=75, yend=125, slitwidth_mm=1.0):
        """Measurement object for the ihr320 + SynapseEM
        """
        self.meta_data = {'exposure': exposure_in_s,
                          'grating': grating,
                          'numavgs': numavgs,
                          'ystart': ystart,
                          'yend': yend,
                          'slitwidth_mm': slitwidth_mm,
                          'center_wl': center_wl,
                          }

        self.scan_instrument_name = name
        self.ihr320 = ihr320.ihr320()
        self.ihr320.center_wavelength = center_wl
        self.ihr320.slit_width = slitwidth_mm
        self.ihr320.turret = grating


        opt = { 
                'IntegrationTime_in_s': exposure_in_s,
                'areaNum': 1,
                'XOrigin': 1,
                'YOrigin': ystart + 1,
                'XSize': 1600,
                'YSize': yend + 1,
                'XBin': 1,
            }
        self.synapseEM = synapseEM_barebones.synapseEM_barebones(**opt)

        x, y = self.synapseEM.COM.GetChipSize()
        self.wavelengths = np.zeroes(len(x))
        self.spectrum_counts = np.zeroes(len(x))

    def measure(self):
        for i in range(self.meta_data['numavgs']):
            self.spectrum_counts += self.synapseEM.acquire()

        self.spectrum_counts = self.spectrum_counts/self.meta_data['numavgs']
        data = {'wavelengths': self.wavelengths, 'spec': self.spectrum_counts}
        self.spectrum_counts = np.zeroes_like(self.wavelengths)
        return data

    def close(self):
        self.synapseEM.close()
        self.ihr320.close()
        del self.synapseEM
        del self.ihr320
