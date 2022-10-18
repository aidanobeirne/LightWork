import win32com.client as wc

#TODO
# add IsReady to programmatically block communication

class synapseEM():
    def __init__(self, ProgId='JYCCD.JYMCD.1', UniqueId='CCD1'):
        wc.pythoncom.CoInitialize()
        self.COM = wc.Dispatch(ProgId)
        self.COM.UniqueID = UniqueId
        self.COM.OpenCommunications()
        self.COM.initialize()
    
    @property
    def center_wavelength(self):
        return self.COM.GetCurrentWavelength()
    @center_wavelength.setter
    def center_wavelength(self, value):
        self.COM.MoveToWavelength(float(value))


    def close(self):
        self.COM.CloseCommunications()
        self.COM.Uninitialize()
    
