# -*- coding: utf-8 -*-

import visa
import time
import os
import numpy as np


class Acton():
    def __init__(self, com_number=11):
        self.pos_filname = os.path.join(os.getcwd(), 'acton_position_tracking.pkl')
        rm = visa.ResourceManager()
        self.VISA = rm.open_resource('ASRL'+str(com_number)+'::INSTR', timeout=10000, read_termination='ok\r\n', write_termination='\r')
        self.wavelength_nm
        self.active_grating
        
    def close(self):
        self.VISA.clear()
        self.VISA.close()
        
    @property
    def wavelength_nm(self):
        try:
            self.VISA.clear()
            value = float(self.VISA.query('?NM').split('nm')[0])
            self._wavelength_nm = value
            return value
        except ValueError:
            return 'Unable to query'
    @wavelength_nm.setter
    def wavelength_nm(self, value):
        self.VISA.clear()
        try:
            self.VISA.write("{} NM".format(value))
            real_position = -100 # random number that will never exit the while loop on the first iteration
            while abs(real_position - value) > 0.05:
                try:
                    self.VISA.clear()
                    real_position = float(self.VISA.query('?NM').split('nm')[0])
                    time.sleep(0.05)
                except ValueError:
                    time.sleep(0.05)
        except visa.VisaIOError:
            print('You changed the poor Acton by a lot of nanometers, please give it time even after the thread is released')
            time.sleep(3)
            pass 
        self._wavelength_nm = real_position
        
    @property
    def active_grating(self):
        self.VISA.clear()
        return int(self.VISA.query('?GRATING'))
    @active_grating.setter
    def active_grating(self, value):
        self.VISA.clear()
        print("Setting Acton active grating to {}".format(value))
        self.VISA.write("{} GRATING".format(int(value)))
        self._active_grating = value
        
    @property
    def speed_nm_per_min(self):
        try:
            self.VISA.clear()
            return float(self.VISA.query('?NM/MIN').split('nm/min')[0])
        except ValueError:
            return 'Unable to query'
    @speed_nm_per_min.setter
    def speed_nm_per_min(self, value):
        self.VISA.clear()
        print("Setting Acton speed to {} nm/min".format(value))
        self.VISA.write("{} NM/MIN".format(int(value)))
        self._speed_nm_per_min = value
    
    def calibrate(self, filepath, filename, acton_wavelengths, andor_wavelengths, camera, take_dark=False, plot=True):    
        if not os.path.exists(os.path.join(filepath, 'Acton_wavelength_calibration')):
            os.makedirs(os.path.join(filepath, 'Acton_wavelength_calibration'))
        if take_dark:
            input('Please turn excitation off to measure dark spectrum. Press Enter')
            camera.StartAcquisition()
            data = []
            camera.GetAcquiredData(data)
            dark_spectrum = data
        else:
            dark_spectrum = None
            
        input('Reveal excitation. Press Enter to continue')
        
        self.calibspectra = []
        for wl in list(acton_wavelengths):
            print('moving to {}nm'.format(wl))
            self.wavelength_nm = wl
            print('acquiring spec')
            camera.StartAcquisition()
            data = []
            camera.GetAcquiredData(data)
            spectrum = data
            if np.max(data) > 65000:
                print('CCD saturated at {}nm, lower exposure and rerun the scan'.format(wl))
                break
            self.calibspectra.append(spectrum)
        center_wls = []
        for spec in self.calibspectra:
            center_wls.append(andor_wavelengths[spec.index(max(spec))]) 
        wavelength_correction_values_in_nm = np.array(center_wls-np.array(acton_wavelengths))
        
        np.savez(os.path.join(filepath, 'Acton_wavelength_calibration', filename), andor_wavelengths=andor_wavelengths, acton_wavelengths=acton_wavelengths, 
                 spectra=self.calibspectra, dark_spectrum=dark_spectrum, wavelength_correction_values_in_nm=wavelength_correction_values_in_nm)
        
        if plot:
            plt.close('all')   
            
            plt.figure()
            plt.contourf(andor_wavelengths, acton_wavelengths, self.calibspectra, 500)
            plt.title('Measured spectra')
            plt.xlabel('andor wavelengths (nm)')
            plt.ylabel('acton wavelengths (nm)');
            
            plt.figure()
            plt.plot(acton_wavelengths, acton_wavelengths,'r--', label = 'Expected values' )
            plt.scatter(acton_wavelengths, center_wls, label = 'Measured center wavelengths');
            plt.title('Center wavelengths of Acton vs Andor measured centered wavelengths')
            plt.xlabel('andor wavelengths (nm)')
            plt.legend()
            plt.ylabel('acton wavelengths (nm)');
            
            plt.figure()
            plt.scatter(acton_wavelengths, np.array(center_wls)-np.array(acton_wavelengths))
            plt.title('Difference between measured and expected center wavelengths')
            plt.xlabel('andor wavelengths (nm)')
            plt.ylabel('$\Delta$ (nm)');
        

#%%
if __name__=='__main__':
    import datetime
    import sys
    import signal
    from Andor.andor import Andor
    import matplotlib.pyplot as plt
    
# =============================================================================
#     Andor spectrometer initialization
# =============================================================================
    exposure = 0.001 #seconds
    hlength = 1024
    v_cent = 128
    v_height = 26
    # Andor Camera Wavelengths - I hate this, but i havent quite gotten the Shamrock Python calibration functioning just yet...
    import csv
    andor_wavelengths = []
    with open(r'C:\Users\HeinzLab\Documents\Aidan\Python\X-axis\884p25_cwl.asc') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            andor_wavelengths.append(float(row[0]))

    cam = Andor()
    
    def signal_handler(signal, frame):
        print('Shutting down the camera...')
        cam.ShutDown()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    cam.SetReadMode(3) # Single track mode (3) is FVB over a defined pixel height
    cam.SetSingleTrack(128, 13) # int center, int height
    cam.SetAcquisitionMode(1) # Single Scan 
    cam.SetTriggerMode(0) # Internal trigger
    cam.SetShutter(1,1,0,0)  # shutter always open
    cam.SetPreAmpGain(0) # Don't think this is necessary
    cam.SetEMCCDGain(1) # Don't think this is necessary
    cam.SetExposureTime(exposure)
    cam.SetCoolerMode(1) # Maintain set temperature after ShutDown method is called
    cam.SetTemperature(-89)
    cam.CoolerON()
    while 'DRV_TEMP_STABILIZED' not in cam.GetTemperature():
        print( "Temperature is:" + str(cam.temperature))
        print(cam.GetTemperature())
        time.sleep(10)   
    print('STABILIZED')

# =============================================================================
# Acton stuffs
#     Acton Grating info
#     1. 1200 gr/mm BLZ 500 nm - good from 400 nm to 650 nm (above 60% efficiency)
#     2. 600 gr/mm BLZ 500 nm - good from 350 nm to 700 nm (above 60% efficiency)
#     3. 600 gr/nm BLZ  1000 nm - good from  750 nm to 1400 nm (above 60% efficiency)
# =============================================================================
    acton = Acton()
    acton.active_grating = 3
    acton_wavelengths = np.arange(801, 960+1, 1) #np.arange(867, 887, 1)
    acton.calibrate(
        filepath=os.path.dirname(os.path.realpath(__file__)),
        filename='Acton_calibration_spectra_{}.npz'.format(datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")).replace(':', '-'),
        andor_wavelengths=andor_wavelengths,
        acton_wavelengths=acton_wavelengths,
        camera=cam,
        take_dark=False,
        plot=True
        )
    cam.ShutDown()

        