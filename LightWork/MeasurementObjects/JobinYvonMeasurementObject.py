import sys
import os

# Old JY, Synapse, and InGaAs camera fucntions... they're ugly but they work, so i wont try to change them.
from LightWork.ParentClasses.OldJYScripts.spectra import SingleSpectrum
from LightWork.ParentClasses.OldJYScripts.acquire import *
from LightWork.ParentClasses.OldJYScripts.synapse import *
from LightWork.ParentClasses.OldJYScripts.ccd3000_visa import *


class JobinYvonMeasurementObject():
    def __init__(self, name='Jobin Yvon', exposure_in_s=1, grating=1, use_synapse=1, numavgs=1, center_wl=700,
                 ystart=125, yend=165, slitwidth_mm=1.0):
        """Measurement object for the entire Jobin Yvon spectrometer + Synergy CCD + InGaAs camera.

        Args:
            name (str, optional): custom name for measurement object. Defaults to 'Jobin Yvon'.
            exposure_in_s (int, optional): exposure in seconds. Defaults to 1.
            grating (int, optional): 0 is 1200 g/mm 500nm blaze, 
                                     1 is 150 g/mm with 500nm blaze, 
                                     2 is 150 g/mm with 1200nm blaze. Defaults to 1.
            use_synapse (int, optional): whether to use the synapse or InGaAs. Defaults to 1.
            numavgs (int, optional): number of acquisitions to take and average over. Defaults to 1.
            center_wl (int, optional): center wavelength of spectrum. Defaults to 700.
            ystart (int, optional): bottom-most pixel to integrate over. Defaults to 125.
            yend (int, optional): top-most pixel to integrate over. Defaults to 165.
            slitwidth_mm (float, optional): slit width in mm. Defaults to 1.0.
        """
        self.meta_data = {'exposure': exposure_in_s,
                          'grating': grating,
                          'numavgs': numavgs,
                          'ystart': ystart,
                          'yend': yend,
                          'slitwidth_mm': slitwidth_mm,
                          'center_wl': center_wl,
                          'use_synapse': use_synapse
                          }

        self.scan_instrument_name = name

        # Some really ugly initialization code below that i adapted...
        if use_synapse:
            self.camera = initsynapse()
        else:
            self.camera = initccd3000_visa()
        self.JY = initmono()
        mono_setgrating(self.JY, grating)

        self.open_shutter()

        (ccd, spectrum, queryfn) = acqsetup2(self.meta_data['use_synapse'], self.camera, self.JY,
                                             center_wl, exposure_in_s*1e-3, numavgs, ystart, yend, slitwidth_mm)
        self.wavelengths = spectrum.wavelengths

    def measure(self):
        spec = acquire(self.meta_data['use_synapse'], self.camera, self.JY, self.meta_data['center_wl'], self.meta_data['exposure']*1e3,
                       self.meta_data['numavgs'], self.meta_data['ystart'], self.meta_data['yend'],
                       'Target spectrum', False, self.meta_data['slitwidth_mm']).counts
        data = {'wavelengths': self.wavelengths, 'spec': spec}
        return data

    def open_shutter(self):
        shutter_open = bool(1)
        count = 12
        while not(shutter_open):
            ihr_shutter(self.camera, False)
            ihr_shutter(self.camera, True)
            UI = 0
            count = count-1
            shutter_open = bool(shutter_open+bool(UI)+(bool(count)))

    def close(self):
        pass
