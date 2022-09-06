# =============================================================================
# Not sure how to deal with the signal_handler function, so for now I will not inherit the Andor class, but just write a wrapper around it
# =============================================================================
import time
import sys
import numpy as np
import LightWork.ParentClasses.Andor.andor as andor
import signal


class AndorMeasurementObject():
    def __init__(self, name='andor', exposure_in_s=1, numavgs=1, vcent=120, vheight=21, AcquisitionMode=1, PreAmpGain=1.0, Readmode=3, temperature=-89, wait_to_cool=True, path_to_domain=None):
        """Measurement object for the Newton andor Si CCD. Note that this class does not control the Shamrock spectrometer. To use this MeasurementObject, first open
        Andor Solis software and set the spectrometer parameters to whatever you desire. Then close Solis and click 'save' when prompted to save acquisition settings. Once 
        Solis is closed, you can use this class to acquire data.

        Args:
            name (str, optional): custom name for measurement object. Defaults to 'andor'.
            exposure_in_s (float, optional): exposure time in seconds. Defaults to 1.
            numavgs (int, optional): number of acquisitions to take and average over. Defaults to 1.
            vcent (int, optional): center integration pixel. Defaults to 120.
            vheight (int, optional): pixel height over which to integrate. Defaults to 21.
            AcquisitionMode (int, optional): Camera acquisition mode. Defaults to 1.
            Readmode (int, optional): Camera Readmode. Defaults to 3.
            temperature (int, optional): Camera temperature. Defaults to -89.
            wait_to_cool (bool, optional): Whether or not to hold the kernel and wait for the camera to cool down. Defaults to True.
            path_to_domain (_type_, optional): path to a csv containing the domain of the spectrum. Unfortunately we cannot pull the domain directly
            from the shamrock in the current form. Defaults to None.
        """
        self.meta_data = {'exposure': exposure_in_s,
                          'vcent': vcent,
                          'vheight': vheight,
                          'numavgs': numavgs,
                          'AcquisitionMode': AcquisitionMode,
                          'Readmode': Readmode,
                          'temperature': temperature,
                          'PreAmpGain': PreAmpGain
                          }

        self.scan_instrument_name = name
        self.cam = andor.Andor()
        signal.signal(signal.SIGINT, self.signal_handler)
        self.cam.SetTriggerMode(0)
        self.cam.SetShutter(1, 1, 0, 0)
        self.cam.SetPreAmpGain(PreAmpGain)
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
                print("\rTemperature is = {}C, status is = {}".format(
                    self.cam.temperature, self.cam.GetTemperature()), end='\r', flush=True)
                time.sleep(10)
            print()
            print('STABILIZED')

    def measure(self):
        if self.meta_data['numavgs'] > 1:
            spectra = []
            for i in range(self.meta_data['numavgs']):
                self.cam.StartAcquisition()
                spec = []
                self.cam.GetAcquiredData(spec)
                spectra.append(spec)
            spec = np.mean(spectra, axis=0)
        else:
            self.cam.StartAcquisition()
            spec = []
            self.cam.GetAcquiredData(spec)
        data = {'wavelengths': self.wavelengths, 'spec': spec}
        return data

    def signal_handler(self, signal, frame):
        print('Shutting down the camera...')
        self.cam.ShutDown()
        sys.exit(0)

    def close(self):
        self.cam.ShutDown()

    @property
    def binning(self):
        return self.meta_data['vcent'], self.meta_data['vheight']

    @binning.setter
    def binning(self, vcent, vheight):
        self.cam.SetSingleTrack(vcent, vheight)
        self.meta_data['vcent'] = vcent
        self.meta_data['vheight'] = vheight

    @property
    def exposure(self):
        return self.meta_data['exposure']

    @exposure.setter
    def exposure(self, exposure_in_s):
        self.cam.SetExposureTime(exposure_in_s)
        self.meta_data['exposure'] = exposure_in_s

    @property
    def PreAmpGain(self):
        return self.meta_data['PreAmpGain']

    @PreAmpGain.setter
    def PreAmpGain(self, gain):
        self.cam.SetPreAmpGain(gain)
        self.meta_data['PreAmpGain'] = gain

    @property
    def Temperature(self):
        return self.meta_data['temperature']

    @Temperature.setter
    def Temperature(self, temp):
        self.cam.SetTemperature(temp)
        self.meta_data['temperature'] = temp

    @property
    def numavgs(self):
        return self.meta_data['numavgs']

    @numavgs.setter
    def numavgs(self, num):
        self.meta_data['numavgs'] = num

    # @property
    # def Accumulations(self):
    #     return self.meta_data['accumulations']

    # @Accumulations.setter
    # def Accumulations(self, num):
    #     self.cam.SetNumberAccumulations(num)
