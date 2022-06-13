from SimpleScan.MeasurementObjects.JobinYvonMeasurementObject import JobinYvonMeasurementObject
from SimpleScan.ScanObjects.KeithleyScanObject import KeithleyScanObject
from SimpleScan.SimpleScan import Simplescan
cam = JobinYvonMeasurementObject(exposure_in_s=1, grating=1, use_synapse=1, numavgs=1, center_wl =700, ystart=125, yend=165, slitwidth_mm=1.0)
topgate = KeithleyScanObject(address ='58', name='TG', compliance_current=300e-9, scan_values=np.arange(-1, 1.25, 0.25), scan_nest_index=0)
backgate = KeithleyScanObject(address ='59', name='BG', compliance_current=300e-9, scan_values=np.arange(-1, 1.25, 0.25), scan_nest_index=0)


Measurement = SimpleScan(
     measurement_instrument=cam, scan_instruments=[topgate, backgate], laser_shutter=False,
     savepath=r"C:\Users\heinz\Documents\User Files\aidan\simpleSweeptest\{}/".format(date.today().strftime("%b-%d-%Y")),
     savename='test',scan_notes='', save_npz=0, notify_me=False
     )

Measurement.run_sweep()
    
    






















