import sys
import os

# Old JY, Synapse, and InGaAs camera fucntions... they're ugly but they work, so i wont try to change them.
from SimpleScan.ParentClasses.OldJYScripts.spectra import SingleSpectrum
from SimpleScan.ParentClasses.OldJYScripts.acquire import *
from SimpleScan.ParentClasses.OldJYScripts.synapse import *
from SimpleScan.ParentClasses.OldJYScripts.ccd3000_visa import *
    

class JobinYvonMeasurementObject():
    def __init__(self, exposure_in_s=1, grating=1, use_synapse=1, numavgs=1, center_wl =700, 
                ystart=125, yend=165, slitwidth_mm=1.0):
        self.meta_data = {'exposure': exposure_in_s,
                        'grating': grating,
                        'numavgs': numavgs,
                        'ystart': ystart,
                        'yend': yend,
                        'slitwidth_mm': slitwidth_mm,
                        'center_wl': center_wl
                        }

        self.scan_instrument_name = 'JobinYvon'

        # Some really ugly initialization code below that i adapted...
        if use_synapse:
            self.camera = initsynapse()
        else:
            self.camera = initccd3000_visa()
        self.JY = initmono()
        mono_setgrating(self.JY, grating)

        shutter_open=bool(1)
        count=12
        while not(shutter_open):
            ihr_shutter(self.camera, False)
            ihr_shutter(self.camera,True)
            UI=0#input('Did shutter click open? Enter if not, \'1\' if yes: \n')
            count=count-1
            shutter_open=bool(shutter_open+bool(UI)+(bool(count)))

        print(shutter_open)
        (ccd,spectrum,queryfn)=acqsetup2(use_synapse, self.camera, self.JY, center_wl, exposure_in_s*1e-3, numavgs, ystart, yend, slitwidth_mm)
        self.wavelengths=spectrum.wavelengths
        
            
    def measure(self):
        spec = acquire(1, self.camera, self.JY, self.meta_data['center_wl'], self.meta_data['exposure']*1e-3, 
                self.meta_data['numavgs'], self.meta_data['ystart'], self.meta_data['yend'],
                 'Target spectrum', False, self.meta_data['slitwidth_mm']).counts
        data = {'wavelengths': self.wavelengths, 'spec': spec}
        return data



    def close(self):
        pass


