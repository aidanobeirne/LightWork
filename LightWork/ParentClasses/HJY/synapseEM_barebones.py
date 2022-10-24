import win32com.client as wc

try:
    from LightWork.ParentClasses.HJY.enums import jyUnits, jyUnitsType, jyCCDDataType, jyDeviceOperatingMode
except ModuleNotFoundError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from enums import jyUnits, jyUnitsType, jyCCDDataType, jyDeviceOperatingMode
import time
import numpy as np

#TODO
# OpenShutter and CloseShutter commands -- are they necessary?

class synapseEM_barebones():
    def __init__(self, ProgId='JYCCD.JYMCD.1', UniqueId='CCD1', **kw):
        self.opt = {  # default options
            'IntegrationTime_in_s': 5,
            'ystart': 75,
            'ystop': 125,
        }

        wc.pythoncom.CoInitialize()
        self.COM = wc.Dispatch(ProgId)
        self.COM.UniqueID = UniqueId
        self.COM.Load()
        self.COM.OpenCommunications()
        self.COM.initialize(True, False)
        time.sleep(3)

        self.old_init_protocol()            # Bizarre series of commands that have to be run for the camera to work properly
        self.old_acq_setup2_protocol()      # Bizarre series of commands that have to be run for the camera to work properly (again)
        self.wait = 0.01

        self._process_kw(**kw)
        self.COM.IntegrationTime = self.opt['IntegrationTime_in_s'] * 1e3   

        # pixel number is 1600 in x direction but the SDK throws an error when i use this :(                                                                                   
        self.COM.DefineArea(1,                                           # areaNum - area number being setup
                            1,                                           # XOrigin - Start x coordinate of the area
                            self.opt['ystart'] + 1 ,                     # YOrigin - Start y coordinate of the area
                            1024,                                        # XSize - Size x of the area
                            self.opt['ystop'] - self.opt['ystart'] + 1,  # YSize - Size y of the area
                            1,                                           # XBin - bin factor in x direction
                            self.opt['ystop'] - self.opt['ystart'] + 1)  # YBin - bin factor in y direction


    def _process_kw(self, **kw):
        '''
        process kwargs
        '''
        for key, value in kw.items():
            self.opt[key] = value

    @property
    def integration_time_in_s(self):
        return self.COM.IntegrationTime
    @integration_time_in_s.setter
    def integration_time_in_s(self, value):
        self.COM.IntegrationTime = value

    def acquire(self):
    # Weirdly the only way to acquire without error... dont change this code for now
        if self.COM.ReadyForAcquisition == False:
            print('Synapse not ready!')
            return
        self.COM.StartAcquisition(1)
        # print('acquiring')
        while True:
            if self.COM.AcquisitionBusy() == False:
                break
            time.sleep(self.wait)
        # print('retrieving')
        dat = np.array(self.COM.GetResult().GetFirstDataObject().GetRawData())
        return dat

    def close(self):
        self.COM.CloseCommunications()
        del self.COM

    def old_init_protocol(self):
        print(self.COM.FirmwareVersion)
        print(self.COM.Description)
        print(self.COM.Name)
        x,y = self.COM.GetChipSize()
        print(x,y)
        
        self.COM.SetDefaultUnits(3,13) #(jyutTime, jyuMilliseconds)
        self.COM.IntegrationTime = 10
        #synapse.MultiAcqHardwareMode = False

        # set up for image mode
        self.COM.SelectADC(1) # 1 = 1 MHz
        self.COM.Gain = 1 # 1 = high dynamic range
        self.COM.DefineAcquisitionFormat(0,1) #(0,1) for image, (1,1) for spectrum
        self.COM.DefineArea(1, 1, 1, 1024, 256, 1, 1) 

        print(self.COM.DataSize)
        self.COM.SetOperatingModeValue(1, False) # HW 
        self.COM.NumberOfAccumulations = 1
        self.COM.AcquisitionCount = 1
    
    def old_acq_setup2_protocol(self):
        self.COM.DefineAcquisitionFormat(1,1)
        self.COM.DefineArea(1, 1, 100, 1024, 51, 1, 51)
        self.COM.DataSize
        self.COM.IntegrationTime = 100

    def new_init_protocol(self):
        print('new init protocol')
        self.COM.SetDefaultUnits(jyUnitsType.jyutTime.value, jyUnits.jyuMilliseconds.value)
        print('Unit type enum (3): {}, abbreviation enum (13): {}'.format(jyUnitsType.jyutTime.value, jyUnits.jyuSeconds.value))
        self.COM.SelectADC(1)
        self.COM.Gain = 1
        self.COM.DefineAcquisitionFormat(jyCCDDataType.JYMCD_ACQ_FORMAT_IMAGE.value, 1)
        print('Scan format enum (0): {}'.format(jyCCDDataType.JYMCD_ACQ_FORMAT_IMAGE.value))
        self.COM.DefineArea(1, 1, 1, 1024, 256, 1, 1) 
        self.COM.SetOperatingModeValue(jyDeviceOperatingMode.jyDevOpModeAcqHWTimeBased.value, False)
        print('Hardware Operating Mode enum (1): {}'.format(jyDeviceOperatingMode.jyDevOpModeAcqHWTimeBased.value))
        self.COM.NumberOfAccumulations = 1
        self.COM.AcquisitionCount = 1

        self.COM.DefineAcquisitionFormat(jyCCDDataType.JYMCD_ACQ_FORMAT_SCAN.value, 1)
        print('Scan format enum (1): {}'.format(jyCCDDataType.JYMCD_ACQ_FORMAT_SCAN.value))
        self.COM.DataSize
        self.COM.IntegrationTime = 10

        

        
        
        
        
        
        