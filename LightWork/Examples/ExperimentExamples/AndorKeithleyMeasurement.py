import numpy as np
import datetime
from LightWork.MeasurementObjects.AndorMeasurementObject import AndorMeasurementObject
from LightWork.ScanObjects.KeithleyScanObject import KeithleyScanObject
from LightWork.Measurements import SimpleScan

cam = AndorMeasurementObject(exposure_in_s=1, vcent=135, vheight=21, AcquisitionMode=1,
                             Readmode=3, temperature=-89, wait_to_cool=False, path_to_domain=None)
topgate = KeithleyScanObject(address='58', name='TG', compliance_current=300e-9,
                             scan_values=np.arange(-1, 1.25, 0.25), scan_nest_index=0)
backgate = KeithleyScanObject(address='59', name='BG', compliance_current=300e-9,
                              scan_values=np.arange(-1, 1.25, 0.25), scan_nest_index=0)


Measurement = SimpleScan(
    measurement_instrument=cam, scan_instruments=[
        topgate, backgate], laser_shutter=False,
    savepath=r"C:\Users\HeinzLab\Documents\Aidan\Test\{}/".format(
        datetime.date.today()),
    savename='test', scan_notes='', save_npz=0, notify_me=False
)

Measurement.run_scan()
