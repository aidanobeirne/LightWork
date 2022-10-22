import win32com.client as wc
try:
    from LightWork.ParentClasses.HJY.enums import jyUnits, jyUnitsType, jyCCDDataType
except ModuleNotFoundError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from enums import jyUnits, jyUnitsType, jyCCDDataType
import time
import numpy as np

#TODO
# OpenShutter and CloseShutter commands -- are they necessary?

class synapseEM_barebones():
    def __init__(self, ProgId='JYCCD.JYMCD.1', UniqueId='CCD1', **kw):
        self.opt = {  # default options
            'jyCCDDataType': jyCCDDataType.JYMCD_ACQ_FORMAT_SCAN.value,
            'IntegrationTime_in_s': 5,
            'areaNum': 1,
            'XOrigin': 1,
            'YOrigin': 1,
            'XSize': 1600,
            'YSize': 200,
            'XBin': 1,
            'YBin': 200,
            'ADC': 0,
            'debug': False
        }

        wc.pythoncom.CoInitialize()
        self.COM = wc.Dispatch(ProgId)
        self.COM.UniqueID = UniqueId
        self.COM.Load()
        self.COM.OpenCommunications()
        self.COM.initialize()
        time.sleep(3)
        self._process_kw()

        self.COM.DefineArea(self.opt['areaNum'], 
                            self.opt['XOrigin'],
                            self.opt['YOrigin'],
                            self.opt['XSize'],
                            self.opt['YSize'],
                            self.opt['XBin'],
                            self.opt['YBin'])
        self.COM.IntegrationTime = self.opt['IntegrationTime_in_s']
        self.wait = min(0.01, self.opt['IntegrationTime_in_s']/10)
        print((jyUnitsType.jyutTime.value, jyUnits.jyuSeconds.value))
        self.COM.SetDefaultUnits(jyUnitsType.jyutTime.value, jyUnits.jyuSeconds.value)
        self.COM.SetOperatingModeValue(1,  False)
        self.COM.Gain = 1 #best dynamic range, will add an enum later to fix this
        self.COM.DefineAcquisitionFormat(self.opt['jyCCDDataType'], 1)
        self.COM.SelectADC(self.opt['ADC'])

    def _process_kw(self, *args, **kw):
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
        while True:
            if self.COM.AcquisitionBusy() == False:
                break
            time.sleep(self.wait)
        dat = np.array(self.COM.GetResult().GetFirstDataObject().GetRawData())
        return dat

    def close(self):
        self.COM.CloseCommunications()
