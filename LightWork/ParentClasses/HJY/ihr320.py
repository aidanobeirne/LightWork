import win32com.client as wc
import time

#TODO
# Fix shutter functionality

class ihr320():
    def __init__(self, ProgId='jymono.monochromator', UniqueId='Mono1'):
        wc.pythoncom.CoInitialize()
        self.COM = wc.Dispatch(ProgId)
        self.COM.UniqueID = UniqueId
        self.COM.Load()
        self.COM.OpenCommunications()
        self.COM.initialize(True, False)
        time.sleep(1)
    
    @property
    def center_wavelength(self):
        return self.COM.GetCurrentWavelength()
    @center_wavelength.setter
    def center_wavelength(self, value):
        self.COM.MoveToWavelength(float(value))
        self.blocking_function()

    @property
    def grating(self):
        return self.COM.GetCurrentGrating()[0]
    @grating.setter
    def grating(self, value):
        self.COM.MovetoGrating(float(value))
        self.blocking_function()

    @property
    def turret(self):
        return self.COM.GetCurrentTurret()
    @turret.setter
    def turret(self, value):
        self.COM.MovetoTurret(int(value))
        self.blocking_function()

    @property 
    def slit_width(self, slit_location=0):
        return self.COM.GetCurrentSlitWidth(slit_location)
    @slit_width.setter
    def slit_width(self, value, slit_location=0):
        self.COM.MovetoSlitWidth(slit_location, float(value))
        self.blocking_function()
    # Slit_location options below
    # Front_Entrance = 0, 
    # Side_Entrance =1, 
    # Front_Exit =2, 
    # Side_Exit =3, 
    # First_Intermediate =4, 
    # Second_Intermediate =5

    @property 
    def exit_mirror_position(self):
        return self.COM.GetCurrentMirrorPosition(1)
    @exit_mirror_position.setter
    def exit_mirror_position(self, value):
        # front = 2, side = 3
        self.COM.MovetoMirrorPosition(1, int(value))
        self.blocking_function()

    @property 
    def entrance_mirror_position(self):
        return self.COM.GetCurrentMirrorPosition(0)
    @exit_mirror_position.setter
    def entrance_mirror_position(self, value):
        # front = 2, side = 3
        self.COM.MovetoMirrorPosition(0, int(value))
        self.blocking_function()

    def blocking_function(self):
        print('Changing ihr320 hardware and locking kernel, please wait.')
        while self.COM.IsBusy():
            time.sleep(0.1)
        print('ihr320 hardware change complete')

    # shutter functionality seems to not work right now
    def open_shutter(self):
        self.COM.OpenShutter()

    def close_shutter(self):
        self.COM.CloseShutter()

    def get_shutter_position(self):
        # closed = 0, open = 1
        pos = self.COM.GetCurrentShutterPosition()
        return pos

    def close(self):
        self.COM.CloseCommunications()
    
