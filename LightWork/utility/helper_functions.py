import sys
import os
import numpy as np
import pickle
from functools import reduce
import operator
import matplotlib.pyplot as plt
from itertools import product
import pprint

# Helper functions

def modified_z_score(intensity):
    """calculates the mean absolute deviation and returns the modified z score

    Args:
        intensity (array): dataset usually containing intensity values (such as a spectrum)

    Returns:
        modified z score: an array of datapoints that correspond to outlier strength
    """
    median_int = np.median(intensity)
    mad_int = np.median([np.abs(intensity - median_int)]
                        )  # Mean absolute deviation
    # 0.75th quartile of normal distribution
    modified_z_scores = 0.6745 * (intensity - median_int) / mad_int
    return abs(np.array(modified_z_scores))

def RemoveCosmicRays(spec, m, threshold):
    """Removes cosmic rays from a dataset

    Args:
        spec (array): spectrum
        m (int): number of adjacent points to average over. This average will replace the cosmic ray datapoint with an interpolated point
        threshold (float): the threshold outlier strength that triggers the replacement of a datapoint. this needs to be chosen so that only cosmic rays are above this threshold
    Returns:
        array: the spectrum with cosmic rays removed
    """
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
    """recursively runs the RemoveCosmicRays function. This is often more effective than running the ray removal one time.

    Args:
        spec (array): spectrum
        m (int): number of adjacent points to average over. This average will replace the cosmic ray datapoint with an interpolated point
        threshold (list of floats): RemoveCosmicRays will be run on the spectrum using each threshold in the list

    Returns:
        array: the spectrum with cosmic rays removed
    """
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

def shift_correction_range(spectra, energies, e_min, e_max, shift_value):
    """ Shifts a dataset such that the average of each spectrum over a desired energy range is equal to the shift_value
    Args:
        spectra (array): 
        energies (array): 
        e_min (float): minimum energy of averaging window
        e_max (float): maximum energy of averaging window
        shift_value (float): value to shift spectra to

    Returns:
        _type_: _description_
    """
    temp = []
    idx_max = min(range(len(energies)), key=lambda i: abs(energies[i]-e_min))
    idx_min = min(range(len(energies)), key=lambda i: abs(energies[i]-e_max))
    for spec in spectra:
        offset = np.mean(spec[idx_min:idx_max])
        shift = shift_value - offset
        temp.append(np.array(spec)+shift)
    return temp

def get_from_dict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)

def set_in_dict(dataDict, mapList, value):
    get_from_dict(dataDict, mapList[:-1])[mapList[-1]] = value

def generate_deeplotter_input(experiment, x_key_list, y_key_list, swap_domain_units=False):
    """ Constructs 3D data array that is used as an input to the deeplotter package

    Args:
        experiment (Dict): dictionary from imported LightWork save file
        x_key_list (list): list of strings to navigate to sorter key, e.g. ['keithley_BG, 'voltage [V]']
        y_key_list (list): same as x_key_list but for y value
        swap_domain_units (bool, optional): whether or not to swap the domain from enegy to wavelengths or vice versa. Defaults to False.

    Returns:
        dict: dictionary containing the arguments that go to the deeplotter instance. Just unpack the dictionary to use the output.
    """
    # construct domain
    energies = np.array(experiment['master_data'][0]['data']['wavelengths'])
    if swap_domain_units:
        energies = 1240/energies
    # construct grid of scan values
    xvalues = sorted(set([get_from_dict(scan, x_key_list) for scan in experiment['master_data'].values()]))
    yvalues = sorted(set([get_from_dict(scan, y_key_list) for scan in experiment['master_data'].values()]))
    xcoord, ycoord = np.meshgrid(xvalues, yvalues)
    # reconstruct coordinate array and array of corresponding scan IDs
    idx_grid = np.ones_like(xcoord)
    for x, y in list(product(xvalues, yvalues)):
        for idx, scan in experiment['master_data'].items():
            if get_from_dict(scan, x_key_list) == x and get_from_dict(scan, y_key_list) == y:
                scan_index = idx  
        j = np.argwhere(xcoord == x)[0][1]
        i = np.argwhere(ycoord == y)[0][0]
        idx_grid[i,j] = scan_index
    # construct 3D data array
    data_threeD = np.zeros((len(yvalues), len(xvalues), len(energies)))
    for x, y in list(product(xvalues, yvalues)):
        for idx, scan in experiment['master_data'].items():
            if get_from_dict(scan, x_key_list) == x and get_from_dict(scan, y_key_list) == y: 
                j = np.argwhere(xcoord == x)[0][1]
                i = np.argwhere(ycoord == y)[0][0]
                try:
                    data_threeD[i,j] = experiment['master_data'][idx]['data']['reflection contrast']
                except KeyError:
                    try:
                        data_threeD[i,j] = experiment['master_data'][idx]['data']['spec dark subtracted']
                    except KeyError:
                        data_threeD[i,j] = experiment['master_data'][idx]['data']['spec']       
    xvalues = np.array(xvalues)
    yvalues = np.array(yvalues)
    args = {'x': xvalues, 'y': yvalues, 'z': energies, 'data': data_threeD}
    return args

def add_ref_or_dark_to_experiment(path_to_pkl, ref=None, dark=None):
    """ Adds a reference or dark to a Lightwork savefile and resaves the dataset
    Args:
        path_to_pkl (str): path to LightWork savefile
        ref (array, optional): reference spectrum. Defaults to None.
        dark (array, optional): dark spectrum. Defaults to None.
    """
    # load pickle file
    with open(r"{}".format(path_to_pkl), 'rb') as handle:
        experiment = pickle.load(handle)
    # add spectra to dataset
    for scan in experiment['master_data'].values():
        if dark is not None and ref is not None:
            scan['data']['spec dark subtracted'] = scan['data']['spec'] - np.array(dark)
            scan['data']['reflection contrast'] = (scan['data']['spec'] - np.array(ref)) / (np.array(ref) - np.array(dark))
        elif dark is not None and ref is None:
            scan['data']['spec dark subtracted'] = scan['data']['spec'] - np.array(dark)
        elif dark is None and ref is not None:
            scan['data']['reflection contrast'] = (
                scan['data']['spec'] - np.array(ref)) / np.array(ref)
                # save file
    with open(path_to_pkl, "wb") as f:
            pickle.dump(experiment, f)


def plot_sorter_linecut(experiment, map_to_sorter, sorter_cuts_to_plot=[], title='', legend_var='', cmap='Greys', cr_m=3, cr_thresholds=[], sc_e_min=None, sc_e_max=None, z_min=None, z_max=None):
    """ Plots a 2D map of a Lightwork scan in addition to selected linecuts

    Args:
        experiment (dict): Lightwork dictionary
        map_to_sorter (list): list of strings to navigate to sorter key, e.g. ['keithley_BG, 'voltage [V]']
        sorter_cuts_to_plot (list, optional): sorter values to plot linecuts of (e.g. 3.5 if you want to plot the 3.5 volt spectrum). Defaults to [].
        title (str, optional): title of plot. Defaults to ''.
        legend_var (str, optional): legend variable name. Defaults to ''.
        cmap (str, optional): color map of contourplot
        cr_m (int, optional): cosmic ray removal m value (see CosmicRayRemoval docstring for more info). Defaults to 3.
        cr_thresholds (list, optional): cosmic ray removal thresholds (see CosmicRayRemoval docstring for more info). Defaults to [].
        sc_e_min (float, optional): shift correction energy minimum (see shift_correction_range docstring for more info). Defaults to None.
        sc_e_max (float, optional): shift correction energy maximum (see shift_correction_range docstring for more info). Defaults to None.
        z_min (float, optional): zmin of contourplot. Defaults to None.
        z_max (float, optional): zmax of contourplot. Defaults to None.
    """
    energies = 1240/np.array(experiment['master_data'][0]['data']['wavelengths'])
    spectra = []
    sorter = []
    for scan in experiment['master_data'].values():
        try:
           spectra.append(scan['data']['reflection contrast'])
        except KeyError:
            try:
                spectra.append(scan['data']['spec dark subtracted'])
            except KeyError:
                spectra.append(scan['data']['spec'])  
        sorter.append(get_from_dict(scan, map_to_sorter))
    spectra = np.array(spectra)
    sorter = np.array(sorter)
    if cr_thresholds:
        spectra = RemoveCosmicRaysRecursive(spectra, cr_m, cr_thresholds)
    if sc_e_min is not None:
        shift_correction_range(spectra, energies, sc_e_min, sc_e_max)
    if sorter_cuts_to_plot:
        true_ns = [list(sorter)[(abs(sorter-val)).argmin()]
                   for val in sorter_cuts_to_plot]
    else:
        true_ns = []

    fig, axs = plt.subplots(2, 1)
    for d in true_ns:
        spec = list(spectra)[list(sorter).index(d)]
        axs[1].plot(energies, spec, label='{} = {:.2e}'.format(legend_var, d))
        axs[0].plot(energies, d*np.ones_like(energies), '-', alpha=0.4)
    plt.xlabel('Energy [eV]')
    axs[1].set_xlim((min(energies), max(energies)))
    axs[1].set_ylabel('Intensity [a.u.]')
    axs[1].legend(prop={'size': 10})
    zmin = z_min if z_min is not None else np.min(spectra)
    zmax = z_max if z_max is not None else np.max(spectra)
    contourplot = axs[0].contourf(
        energies, sorter, spectra, levels=np.linspace(zmin, zmax, 500), cmap=cmap)
    axs[0].set_ylabel(map_to_sorter[-1])
    axs[0].set_autoscalex_on(False)
    plt.colorbar(contourplot, ax=axs[0], pad=0.02)
    fig.suptitle(title, fontsize=35)
    plt.show()


# def plot_energy_linecut(master_data, map_to_sorter, title='', energy_cuts_to_plot=[], halfwidth=3, cr_m=3, cr_thresholds=[], sc_e_min=None, sc_e_max=None, z_min=None, z_max=None):
#     energies = 1240/np.array(master_data[0]['data']['wavelengths'])
#     spectra = []
#     sorter = []
#     for step, scan_dict in master_data.items():
#         spectra.append(scan_dict['data']['spec'])
#         sorter.append(getFromDict(scan_dict, map_to_sorter))
#     spectra = np.array(spectra)
#     sorter = np.array(sorter)
#     if cr_thresholds:
#         spectra = RemoveCosmicRaysRecursive(spectra, cr_m, cr_thresholds)
#     if sc_e_min is not None:
#         shift_correction_range(spectra, energies, sc_e_min, sc_e_max)
#     if energy_cuts_to_plot:
#         true_energies = [energies[(abs(energies-val)).argmin()]
#                          for val in energy_cuts_to_plot]

#     fig, axs = plt.subplots(2, 1)
#     for count, d in enumerate(true_energies):
#         idx = list(energies).index(d)
#         axs[1].plot(sorter, np.mean(spectra[:, idx-halfwidth:idx+halfwidth],
#                     axis=1), label='{} eV'.format(np.round(d, 2)), marker='.')
#         axs[0].axvspan(energies[idx-halfwidth], energies[idx +
#                        halfwidth], alpha=0.5, color='C{}'.format(count))
#     plt.xlabel('Energy [eV]')
#     axs[1].set_ylabel('Intensity [a.u.]')
#     axs[1].legend(prop={'size': 10})
#     zmin = z_min if z_min is not None else np.min(spectra)
#     zmax = z_max if z_max is not None else np.max(spectra)
#     contourplot = axs[0].contourf(
#         energies, sorter, spectra, levels=np.linspace(zmin, zmax, 500), cmap='Greys')
#     axs[0].set_ylabel('charge density [cm$^{{-2}}$]')
#     axs[0].set_autoscalex_on(False)
#     plt.colorbar(contourplot, ax=axs[0], pad=0.02)
#     fig.suptitle(title, fontsize=35)
#     plt.show()


