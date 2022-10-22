
from LightWork.ParentClasses.HJY import synapseEM_barebones, ihr320
import numpy as np


class ihr320SynapseEMMeasurementObject():
    def __init__(self, name='ihr320_synapseEM', exposure_in_s=1, grating=1, numavgs=1, center_wl=700, ystart=75, yend=125, slitwidth_mm=1.0, path_to_domain=None):
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

    def measure(self):
        spec = []
        for i in range(self.meta_data['numavgs']):
            spec.append(self.synapseEM.acquire())
        spec = np.mean(spec)
        data = {'wavelengths': self.wavelengths, 'spec': spec}
        return data

    def close(self):
        self.synapseEM.close()
        self.ihr320.close()
        del self.synapseEM
        del self.ihr320
