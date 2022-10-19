import win32com.client as wc
from LightWork.ParentClasses.HJY.enums import jyUnits, jyUnitsType, jyCCDDataType


class synapseEM():
    def __init__(self, ProgId='JYCCD.JYMCD.1', UniqueId='CCD1', **kw):
        self.opt = {  # default options
            'jyCCDDataType': jyCCDDataType.JYMCD_ACQ_FORMAT_Scan.value,
            'IntegrationTime_in_s': 5,
            'verbose':          False
        }

        wc.pythoncom.CoInitialize()
        self.COM = wc.Dispatch(ProgId)
        self.COM.UniqueID = UniqueId
        self.COM.OpenCommunications()
        self.COM.initialize()
        self.COM.SetDefaultUnits(
            jyUnitsType.jyutTime.value, jyUnits.jyuSeconds.value)

    def _process_kw(self, *args, **kw):
        '''
        process args and kwargs
        '''

        for key, value in kw.items():
            self.opt[key] = value

    @property
    def integration_time_in_s(self):
        return self.COM.IntegrationTime

    @integration_time_in_s.setter
    def integration_time_in_s(self, value):
        self.COM.integration_time_in_s = value

    def close(self):
        self.COM.CloseCommunications()
        self.COM.Uninitialize()
