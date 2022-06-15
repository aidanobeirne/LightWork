import sys
import os
import numpy as np
import pickle
from functools import reduce
import operator
import matplotlib.pyplot as plt
import pprint

# Helper functions


def modified_z_score(intensity):
    median_int = np.median(intensity)
    mad_int = np.median([np.abs(intensity - median_int)]
                        )  # Mean absolute deviation
    # 0.75th quartile of normal distribution
    modified_z_scores = 0.6745 * (intensity - median_int) / mad_int
    return abs(np.array(modified_z_scores))


def RemoveCosmicRays(spec, m, threshold):
    spikes = 1*(abs(modified_z_score(np.diff(spec))) > threshold)
    spike_indices = [i for i, val in enumerate(spikes) if val]
    spec_out = spec.copy()
    for idx in spike_indices:
        w2 = []
        if idx+2+m > len(spec):
            w = np.arange(len(spec)-m, len(spec)-1)
        elif idx < m:
            w = np.arange(0, m+1)
        else:
            # we select 2 m + 1 points around our spike
            w = np.arange(idx-m, idx+1+m)
        # From such interval, we choose the ones which are not spikes
        w2 = w[spikes[w] == 0]
        spec_out[idx] = np.mean(spec[w2])  # and we average their values
    return spec_out


def RemoveCosmicRaysRecursive(spec, m, thresholds):
    if np.ndim(spec) == 2:
        temp = []
        for spectrum in spec:
            spec_out = spectrum
            for threshold in thresholds:
                spec_out = RemoveCosmicRays(spec_out, m, threshold)
            temp.append(spec_out)
        return temp
    else:
        spec_out = spec
        for threshold in thresholds:
            spec_out = RemoveCosmicRays(spec_out, m, threshold)
        return spec_out


def shift_correction(spectra):
    temp = []
    for spec in spectra:
        shift = 1 - spec[0]
        temp.append(np.array(spec)+shift)
    return temp


def shift_correction_range(spectra, energies, e_min, e_max):
    temp = []
    idx_max = min(range(len(energies)), key=lambda i: abs(energies[i]-e_min))
    idx_min = min(range(len(energies)), key=lambda i: abs(energies[i]-e_max))
    for spec in spectra:
        offset = np.mean(spec[idx_min:idx_max])
        shift = 0 - offset
        temp.append(np.array(spec)+shift)
    return temp


dbot = 19.8
dtop = 13.9
d1Lbp = 0.7
d2Lbp = 1.2
d3Lbp = 2.1
eps_bn = 3.9
eps_1Lbp = 8.3
eps_2Lbp = eps_1Lbp
eps_3Lbp = eps_1Lbp


def Efield(vtop, vbot, ds, eps_sample):  # using Ouri
    efield = 1e3*(vtop-vbot)/((dbot+dtop)*eps_sample /
                              eps_bn + ds)  # convert to mv/nm
    return efield


def n(vtop, vbot):
    n = -eps_bn*8.85418e-12 / \
        (1.602e-19)*(vtop/(dtop*1e-9) + vbot/(dbot*1e-9))*1e-4  # convert to cm^-2
    return(n)


def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)


def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value


def all_keys(dict_obj):
    ''' This function generates all keys of
        a nested dictionary. 
    '''
    # Iterate over all keys of the dictionary
    for key, value in dict_obj.items():
        yield key
        # If value is of dictionary type then yield all keys
        # in that nested dictionary
        if isinstance(value, dict):
            for k in all_keys(value):
                yield k


def plot_sorter_linecut(master_data, map_to_sorter, sorter_cuts_to_plot=[], title='', cr_m=3, cr_thresholds=[], sc_e_min=None, sc_e_max=None, z_min=None, z_max=None):
    energies = 1240/np.array(master_data[0]['data']['wavelengths'])
    spectra = []
    sorter = []
    for step, scan_dict in master_data.items():
        spectra.append(scan_dict['data']['spec'])
        sorter.append(getFromDict(scan_dict, map_to_sorter))
    spectra = np.array(spectra)
    sorter = np.array(sorter)
    if cr_thresholds:
        print('ok')
        spectra = RemoveCosmicRaysRecursive(spectra, cr_m, cr_thresholds)
    if sc_e_min is not None:
        shift_correction_range(spectra, energies, sc_e_min, sc_e_max)
    if sorter_cuts_to_plot:
        true_ns = [list(sorter)[(abs(sorter-val)).argmin()]
                   for val in sorter_cuts_to_plot]

    fig, axs = plt.subplots(2, 1)
    for d in true_ns:
        spec = list(spectra)[list(sorter).index(d)]
        axs[1].plot(energies, spec, label='n = {:.2e}'.format(d))
        axs[0].plot(energies, d*np.ones_like(energies), '-', alpha=0.4)
    plt.xlabel('Energy [eV]')
    axs[1].set_xlim((min(energies), max(energies)))
    axs[1].set_ylabel('Intensity [a.u.]')
    axs[1].legend(prop={'size': 10})
    zmin = z_min if z_min is not None else np.min(spectra)
    zmax = z_max if z_max is not None else np.max(spectra)
    contourplot = axs[0].contourf(
        energies, sorter, spectra, levels=np.linspace(zmin, zmax, 500), cmap='Greys')
    axs[0].set_ylabel(map_to_sorter[-1])
    axs[0].set_autoscalex_on(False)
    plt.colorbar(contourplot, ax=axs[0], pad=0.02)
    fig.suptitle(title, fontsize=35)
    plt.show()


def plot_energy_linecut(master_data, map_to_sorter, title='', energy_cuts_to_plot=[], halfwidth=3, cr_m=3, cr_thresholds=[], sc_e_min=None, sc_e_max=None, z_min=None, z_max=None):
    energies = 1240/np.array(master_data[0]['data']['wavelengths'])
    spectra = []
    sorter = []
    for step, scan_dict in master_data.items():
        spectra.append(scan_dict['data']['spec'])
        sorter.append(getFromDict(scan_dict, map_to_sorter))
    spectra = np.array(spectra)
    sorter = np.array(sorter)
    if cr_thresholds:
        spectra = RemoveCosmicRaysRecursive(spectra, cr_m, cr_thresholds)
    if sc_e_min is not None:
        shift_correction_range(spectra, energies, sc_e_min, sc_e_max)
    if energy_cuts_to_plot:
        true_energies = [energies[(abs(energies-val)).argmin()]
                         for val in energy_cuts_to_plot]

    fig, axs = plt.subplots(2, 1)
    for count, d in enumerate(true_energies):
        idx = list(energies).index(d)
        axs[1].plot(sorter, np.mean(spectra[:, idx-halfwidth:idx+halfwidth],
                    axis=1), label='{} eV'.format(np.round(d, 2)), marker='.')
        axs[0].axvspan(energies[idx-halfwidth], energies[idx +
                       halfwidth], alpha=0.5, color='C{}'.format(count))
    plt.xlabel('Energy [eV]')
    axs[1].set_ylabel('Intensity [a.u.]')
    axs[1].legend(prop={'size': 10})
    zmin = z_min if z_min is not None else np.min(spectra)
    zmax = z_max if z_max is not None else np.max(spectra)
    contourplot = axs[0].contourf(
        energies, sorter, spectra, levels=np.linspace(zmin, zmax, 500), cmap='Greys')
    axs[0].set_ylabel('charge density [cm$^{{-2}}$]')
    axs[0].set_autoscalex_on(False)
    plt.colorbar(contourplot, ax=axs[0], pad=0.02)
    fig.suptitle(title, fontsize=35)
    plt.show()

####################################### Important part below ##################################################


# Load master data dictionary
file = open(
    r'C:\Users\heinz\Documents\User Files\aidan\simpleSweeptest\Jun-09-2022\test.pkl', 'rb')
sample = pickle.load(file)
file.close()

# Print all keys in master data dictionary
# for key in all_keys(sample):
#    print(key)

# Sort master data dictionary by a specific key
sample['master_data'] = dict(sorted(sample['master_data'].items(
), key=lambda x: x[1]['keithley_BG']['voltage [V]']))

# Plot data
plt.close('all')

# quick and dirty
# energies = 1240/np.array(sample['master_data'][0]['data']['wavelengths'])
# spectra = []
# sorter = []
# for step, scan_dict in sample['master_data'].items():
#     spectra.append(scan_dict['data']['spec'])
#     sorter.append(getFromDict(scan_dict, ['keithley_BG','voltage [V]']))
# spectra = np.array(spectra)
# sorter = np.array(sorter)
# plt.figure()
# plt.contourf(energies, sorter, spectra)

# Better way to plot, but Fianium room computer cannot handle this
plot_sorter_linecut(master_data=sample['master_data'], map_to_sorter=[
                    'keithley_BG', 'voltage [V]'], title='test scan', sorter_cuts_to_plot=[0])
