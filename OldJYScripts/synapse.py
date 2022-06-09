# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 22:09:21 2016

@author: heinz
"""

import win32com.client as wc
import time
import numpy as np
#import pdb
#from spectra import SingleSpectrum


def initsynapse(force_reinit = True):
    
    wc.pythoncom.CoInitialize()
#    pdb.set_trace()
    synapse = wc.Dispatch('JYCCD.JYMCD')
    print(synapse.GetComponentVersion())
    synapse.Uniqueid = "CCD2" 
    synapse.Load()
    synapse.OpenCommunications()
    #time.sleep(1)

    synapse.Initialize(force_reinit,False) # first param is force reinit. 
    # Initialize() starts a thread. in theory, need to check if it's done before moving on. 
    time.sleep(3)

    print(synapse.FirmwareVersion)
    print(synapse.Description)
    print(synapse.Name)
    x,y = synapse.GetChipSize()
    print(x,y)
    
    synapse.SetDefaultUnits(3,13) #(jyutTime, jyuMilliseconds)
    synapse.IntegrationTime = 10
    #synapse.MultiAcqHardwareMode = False

    # set up for image mode
    synapse.SelectADC(1) # 1 = 1 MHz
    synapse.Gain = 1 # 1 = high dynamic range
    synapse.DefineAcquisitionFormat(0,1) #(0,1) for image, (1,1) for spectrum
    synapse.DefineArea(1, 1, 1, 1024, 256, 1, 1) 

    print(synapse.DataSize)
    synapse.SetOperatingModeValue(1,False) # HW 
    synapse.NumberOfAccumulations = 1
    synapse.AcquisitionCount = 1

    
    return synapse

# spec is 1 for spectrum acquisition mode, 0 for image acquisition mode
def synapse_roi(synapse, spec, xs, ys, xw, yw, xbin, ybin):
    synapse.DefineAcquisitionFormat(spec,1)
    synapse.DefineArea(1, xs, ys, xw, yw, xbin, ybin)
    synapse.DataSize
    

synapse_busydelay = 0.1
def synapse_exp(synapse, exposure):
    synapse.IntegrationTime = exposure
    global synapse_busydelay
    synapse_busydelay = min(0.01, exposure/10/1000)

def getname(ccd):
    if hasattr(ccd,'Name'):
        return ccd.Name
    else:
        return 'CCD3000 VISA'

    
def querysynapse(synapse, shutter=None):
    if synapse.ReadyForAcquisition == False:
        print('Synapse not ready!')
        return
    
    
    # bright collect
    synapse.StartAcquisition(1)
    while True:
        if synapse.AcquisitionBusy() == False:
            break
        time.sleep(synapse_busydelay)
    bright = np.array(synapse.GetResult().GetFirstDataObject().GetRawData())

    
    return bright

        
def ihr_shutter(ccd, shutter_open):
    if hasattr(ccd,'Name'): # it's controlled via win32
        if shutter_open:
            ccd.OpenShutter()
        else:
            ccd.CloseShutter()
    else: # else it's visa
        ccd.read_termination = 'o'
        if shutter_open:
            ccd.query('Z320,0,1\x0d')
        else:
            ccd.query('Z320,0,0\x0d')
        