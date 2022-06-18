# =============================================================================
# Not sure how to deal with the signal_handler function, so for now I will not inherit the Andor class, but just write a wrapper around it 
# =============================================================================
import time
import sys
import os
import LightWork.ParentClasses.Andor.andor as andor
import signal



class AndorMeasurementObject():
    def __init__(self, name='andor', exposure_in_s=1, vcent=120, vheight=21, AcquisitionMode=1, Readmode=3, temperature=-89, wait_to_cool=True, path_to_domain=None):
        self.meta_data = {}
        self.meta_data['exposure'] = exposure_in_s
        self.meta_data['vcent'] = vcent
        self.meta_data['vheight'] = vheight
        self.scan_instrument_name = name
        self.cam = andor.Andor()
        signal.signal(signal.SIGINT, self.signal_handler)
        self.cam.SetTriggerMode(0)
        self.cam.SetShutter(1,1,0,0) 
        self.cam.SetPreAmpGain(0)
        self.cam.SetEMCCDGain(1)
        self.cam.SetCoolerMode(1)
        self.cam.SetReadMode(Readmode) 
        self.cam.SetSingleTrack(vcent, vheight)
        self.cam.SetAcquisitionMode(AcquisitionMode)
        self.cam.SetExposureTime(exposure_in_s)
        self.cam.SetTemperature(temperature)
        self.cam.CoolerON()

        if path_to_domain is not None:
            import csv
            self.wavelengths = []
            with open(r'{}'.format(path_to_domain)) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                for row in spamreader:
                    self.wavelengths.append(float(row[0]))
        else:
            self.wavelengths = 0

        if wait_to_cool:
            while 'DRV_TEMP_STABILIZED' not in self.cam.GetTemperature():
                print("\rTemperature is = {}C, status is = {}".format(self.cam.temperature, self.cam.GetTemperature()), end='\r', flush=True)
                time.sleep(10) 
            print()  
            print('STABILIZED')
            
    def measure(self):
        self.cam.StartAcquisition()
        spec = []
        self.cam.GetAcquiredData(spec)
        data = {'wavelengths':self.wavelengths, 'spec':spec}
        return data

    def signal_handler(self, signal, frame):
        print('Shutting down the camera...')
        self.cam.ShutDown()
        sys.exit(0)
        
    def close(self):
        pass