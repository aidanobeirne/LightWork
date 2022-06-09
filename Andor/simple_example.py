
for name in dir():
    if not name.startswith('_'):
        del globals()[name]
        
from andor import *
import time
import sys
import signal

import matplotlib.pyplot as plt
import matplotlib.colors as colors

import numpy as np
import scipy as sc
from scipy.interpolate import interp1d
import time
import signal
import matplotlib.pyplot as plt
import datetime
import pickle
import os
import visa
import struct


#####################
# Initial settings  #
#####################

#please set these values accordingly!! I have no idea what is used for our cameras!! especially Tset
Tset = -70# -70
EMCCDGain = 1
PreAmpGain = 0
exposure    = 1 #seconds
center_wl   = 910 # 671#

start_px = 115
end_px = 150

def signal_handler(signal, frame):
    print('Shutting down the camera...')
    cam.ShutDown()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Initialising the Camera
cam = Andor()
#cam.SetSingleScan()
cam.SetReadMode(0) # 0 integrates alls pixels
#cam.SetReadMode(4) #sets image mode
#cam.SetImage(1,end_px-start_px+1,1,1024,start_px,end_px)
cam.SetAcquisitionMode(1)
cam.SetTriggerMode(7)
cam.SetShutter(1,1,0,0) #I DON"T KNOW WHAT THIS DOES
cam.SetPreAmpGain(PreAmpGain)#I DON"T KNOW WHAT THIS DOES
cam.SetEMCCDGain(EMCCDGain)#I DON"T KNOW WHAT THIS DOES
cam.SetExposureTime(exposure)
cam.SetCoolerMode(1)
cam.SetTemperature(Tset)
cam.CoolerON()

while cam.GetTemperature() is not 'DRV_TEMP_STABILIZED':
    print( "Temperature is:" + str(cam.temperature))
    print(cam.GetTemperature())
    time.sleep(10)

i = 0

while True:
    i += 1

    print(cam.GetTemperature())
    print(cam.temperature)
    print("Ready for Acquisition")
    cam.StartAcquisition()
    data = []
    cam.GetAcquiredData(data)
    
    plt.figure(10101)
    plt.clf()
    plt.plot(data)
    plt.show()
    plt.pause(0.1)
    
#CLOSE communication with Andor
print('Shutting down the camera...')
cam.ShutDown()
    
#        time.sleep(10)
        #cam.SaveAsBmpNormalised("%03g.bmp" %i)
        #cam.SaveAsBmp("%03g.bmp" %i)
        #cam.SaveAsTxt("%03g.txt" %i)
