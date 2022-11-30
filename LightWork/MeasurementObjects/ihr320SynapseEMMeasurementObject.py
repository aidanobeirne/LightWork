
from LightWork.ParentClasses.HJY import synapseEM_barebones, ihr320
import numpy as np
import csv


class ihr320SynapseEMMeasurementObject():
    def __init__(self, name='ihr320_synapseEM', exposure_in_s=1, grating=3, numavgs=1, center_wl=750, ystart=75, yend=125, slitwidth_mm=2.0, path_to_domain=None):
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
        self.ihr320.turret = int(grating - 1) # Grating labels on spectrometer start indexing at 1 instead of zero

        if path_to_domain is not None:
            wls = []
            with open(r"{}".format(path_to_domain)) as f:
                reader = csv.reader(f, delimiter = '\t')
                for count, row in enumerate(reader):
                    if count == 0:
                        continue
                    wls.append(float(row[0]))
            self.wavelengths = np.array(wls[0:1024])
        else:
            self.wavelengths = None

        opt = {  # default options
            'IntegrationTime_in_s': exposure_in_s,
            'ystart': ystart,
            'ystop': yend,
        }
        self.synapseEM = synapseEM_barebones.synapseEM_barebones(**opt)

    def measure(self):
        if self.meta_data['numavgs'] > 1:
            print('averaging {} times'.format(self.meta_data['numavgs']))
            spectra = []
            for i in range(self.meta_data['numavgs']):
                spectra.append(self.synapseEM.acquire())
            spec = np.mean(spectra, axis=0)
        else:
            spec = self.synapseEM.acquire()
        data = {'wavelengths': self.wavelengths, 'spec': spec}
        return data

    def close(self):
        self.synapseEM.close()
        self.ihr320.close()
        del self.synapseEM
        del self.ihr320
