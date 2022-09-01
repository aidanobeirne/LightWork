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

opt = {  # default options
            'spec_staggering':  0,  # amount to displace spectra by
            'legend_label':     'voltage',
            'hovering_range':     None,
            'title':            'title',  # plot title
            'xlabel':           'x',
            'ylabel':           'y',
            'ilabel':           'intensity [a.u.]',
            'cmap':             'inferno',
            'cr_m':             3,
            'cr_thresholds':    [],
            'sc_e_min':         None,
            'sc_e_max':         None,
            'shift_value':      0,
            'change_x_units':   False,
            'vmin':             None,
            'vmax':             None,
            'display_specs':    [],  # for clicking spectra function
            'xyhoveri':         [0, 0],  # for on_move
            'verbose':          False
        }

plot = h.ShallowPlotter(measurement, ['keithley_TG', 'voltage [V]'], **opt)