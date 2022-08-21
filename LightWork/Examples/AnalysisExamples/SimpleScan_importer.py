import pickle
import matplotlib.pyplot as plt
import numpy as np
import LightWork.utility.helper_functions as h

#%% If you would like to add a reference or dark to the file
ref = np.load(r'SimpleScandat\ref.npz')['spec']
dark = np.load(r'SimpleScanDat\dark.npz')['spec']
h.add_ref_or_dark_to_measurement(r'SimpleScanDat\example.pkl')
#%% Load and plot data
with open(r'SimpleScanDat\example.pkl', 'rb') as handle:
        measurement = pickle.load(handle)
plt.close('all')
h.plot_sorter_linecut(measurement, ['keithley_TG', 'voltage [V]'], sorter_cuts_to_plot=[3.9, 4, 4.2], title='example', legend_var='voltage', cr_m=3, cr_thresholds=[], sc_e_min=None, sc_e_max=None, z_min=None, z_max=None)