import numpy as np
import os
from LightWork.ScanObjects.TestScanObject import TestScanObject
from LightWork.MeasurementObjects.TestMeasurementObject import TestMeasurementObject
from LightWork.SimpleScan import SimpleScan

measurer = TestMeasurementObject()
scanner1 = TestScanObject(name='1', scan_values=np.arange(0,10,1), scan_nest_index=0)
scanner2 = TestScanObject(name='2', scan_values=np.arange(10,20,1), scan_nest_index=0)
scanner3 = TestScanObject(name='3', scan_values=np.arange(30,31,0.1), scan_nest_index=1)
scanner4 = TestScanObject(name='4', scan_values=np.arange(0.1,1.2,0.2), scan_nest_index=2)

Measurement = SimpleScan(
   measurement_instrument=measurer, scan_instruments=[scanner1, scanner2, scanner3], laser_shutter=False,
   savepath= os.path.join(os.getcwd(),'test'),
   savename='test', scan_notes='', save_npz=0, save_at_every_step=False
   )
print(Measurement.scan_values)
Measurement.run_sweep()
    
    






















