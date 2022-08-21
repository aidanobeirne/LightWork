import numpy as np
import os
from LightWork.ScanObjects.SolsTiSScanObject import SolsTiSScanObject
from LightWork.MeasurementObjects.SR830MeasurementObject import SR830MeasurementObject
from LightWork.Measurements import SimpleScan

# Time Constant settings are coded as follows:
# 0 : 10e-6,  1 : 30e-6,   2 : 100e-6,  3 : 300e-6,  4 : 1e-3,  5 : 3e-3,
# 6 : 10e-3,  7 : 30e-3,   8 : 100e-3,  9 : 300e-3, 10: 1,       11: 3,
# 12: 10,    13: 30,    14: 100,    15: 300,  16: 1000,   17: 3000,
#  18: 10000,    19: 30000
#  Sensitivity settings are coded as follows:
# 0 : '2 nV/fA',  1 : '5 nV/fA',  2 : '10 nV/fA',   3 : '20 nV/fA',  4 : '50 nV/fA',
#  5 : '100 nV/fA', 6 : '200 nV/fA', 7 : '500 nV/fA',  8 : '1 uV/pA',  9 : '3 uV/pA',
# 10: '5 uV/pA', 11: '10 uV/pA', 12: '20 uV/pA', 13: '50 uV/pA',  14: '100 uV/pA',
#  15: '200 uV/pA', 16: '500 uV/pA',  17: '1 mV/nA',    18: '2 mV/nA',   19: '5 mV/nA',
#   20: '10 mV/nA', 21: '20 mV/nA', 22: '50 mV/nA', 23: '100 mV/nA', 24: '200 mV/nA',
#  25: '500 mV/nA',   26: '1V/uA'
#

LockIn = SR830MeasurementObject(
    port='GPIB0::11::INSTR', TC=9, sens=21, TCs_to_wait=9.23, navg=50)
solstis = SolsTiSScanObject(address='192.168.1.222', port=39900,
                            scan_values=np.arange(750, 870, 1), scan_nest_index=0)

# First run reference scan
Reference = SimpleScan(
    measurement_instrument=LockIn, scan_instruments=[
        solstis], laser_shutter=False,
    savepath=os.path.join(os.getcwd(), 'test'),
    savename='Reference', scan_notes='', save_npz=0, save_at_every_step=False
)

input('Set offset bias and start chopper to measure reference spectrum. Press Enter')
Reference.run_sweep()

# Change LockIn parameters and run sample scan
LockIn.setTC(13)
LockIn.setsens(8)
LockIn.update_meta_data()
Sample = SimpleScan(
    measurement_instrument=LockIn, scan_instruments=[
        solstis], laser_shutter=False,
    savepath=os.path.join(os.getcwd(), 'test'),
    savename='Sample', scan_notes='', save_npz=0, save_at_every_step=False
)

input('Turn off and remove chopper. Set the AC bias. Press Enter')
Sample.run_scan()
