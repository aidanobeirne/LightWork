
from __future__ import division, print_function, unicode_literals, absolute_import
import numpy as np
import LightWork.utility.helper_functions as h
import matplotlib as mpl
import matplotlib.pyplot as plt
import warnings
import traceback
import sys

try:
    from PyQt5 import QtWidgets
except Exception:
    traceback.print_exc()

# ==========================================================================
# 2D (nonhyperspectral) plotting class
# ==========================================================================


class ShallowPlotter():

    def __init__(self, *args, **kw):
        '''
        input arguments: 
        '''
        self.opt = {  # default options
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
            'change_x_units':   False,
            'vmin':             None,
            'vmax':             None,
            'display_specs':    [],  # for clicking spectra function
            'xyhoveri':         [0, 0],  # for on_move
            'verbose':          False
        }

        self._process_kw(*args, **kw)

        # Axes and Figures
        self.fig, self.axs = plt.subplots(2, 1)
        plt.xlabel(self.opt['xlabel'])
        self.axs[0].set_ylabel(self.opt['ylabel'])
        self.axs[1].set_ylabel(self.opt['ilabel'])
        self.axs[1].set_xlim((min(self.x), max(self.x)))
        self.axs[1].legend(prop={'size': 10})
        vmin, vmax = self.opt['vmin'] if self.opt['vmax'] is not None else (
            np.min(self.data), np.max(self.data))
        self.data = self.data.reshape(self.xx.shape)
        self.colormeshplot = self.axs[0].pcolormesh(
            self.xx, self.yy, self.data, vmin=vmin, vmax=vmax, cmap=self.opt['cmap'], shading='auto')
        # plt.colorbar(self.colormeshplot, ax=self.axs[0], pad=0.02)

        self.fig.suptitle(self.opt['title'], fontsize=35)
        self.lines = {}
        self.specs = {}
        self.legend_vals = {}
        self.shift_is_held = False
        self.u_is_held = False
        self.color_counter = 0
        # events
        self.cids = []
        self.cids.append(self.fig.canvas.mpl_connect(
            'button_press_event', self.onclick))
        self.cids.append(self.fig.canvas.mpl_connect(
            'key_press_event', self.on_key_press))
        self.cids.append(self.fig.canvas.mpl_connect(
            'key_release_event', self.on_key_release))

    def _process_kw(self, *args, **kw):
        '''
        process args and kwargs
        '''

        for key, value in kw.items():
            self.opt[key] = value
        print(len(args))
        # construct data
        if len(args) == 3:
            datavars = ['x', 'y', 'data']
            for i in range(len(args)):
                setattr(self, datavars[i], args[i])
        elif len(args) == 2:
            datavars = ['experiment', 'map_to_sorter']
            for i in range(len(args)):
                setattr(self, datavars[i], args[i])
            self.data = []
            self.y = []
            for scan in self.experiment['master_data'].values():
                try:
                    self.data.append(scan['data']['reflection contrast'])
                except KeyError:
                    try:
                        self.data.append(scan['data']['spec dark subtracted'])
                    except KeyError:
                        self.data.append(scan['data']['spec'])
                self.y.append(h.get_from_dict(scan, self.map_to_sorter))
            self.data = np.array(self.data)
            self.y = np.array(self.y)
            self.x = np.array(scan['data']['wavelengths'])
            self.xx, self.yy = np.meshgrid(self.x, self.y)
            if self.opt['change_x_units']:
                self.x = 1240/self.x
        else:
            raise ValueError('Incorrect data type format')

    def onclick(self, event):
        if self.shift_is_held:
            yidx = (abs(self.y - event.ydata)).argmin()
            yvalue = self.y[yidx]
            self.lines[yvalue] = self.axs[0].axhline(
                yvalue, alpha=0.35, color='C{}'.format(self.color_counter))
            self.specs[yvalue] = self.axs[1].plot(
                self.x, self.data[yidx, :], label='{}={}'.format(self.opt['legend_label'], np.round(yvalue, 2)), color='C{}'.format(self.color_counter))
            self.axs[1].legend(prop={'size': 10})
            self.color_counter += 1

        elif self.u_is_held:
            yidx = (abs(self.y - event.ydata)).argmin()
            yvalue = self.y[yidx]
            current_legend_items = []
            for key in self.lines.keys():
                current_legend_items.append(key)
            key_to_remove = current_legend_items[(
                np.array(current_legend_items) - yvalue).argmin()]

            l = self.lines.pop(key_to_remove)
            l.remove()
            del l
            s = self.specs.pop(key_to_remove)
            s.remove()
            del l

            self.axs[1].legend(prop={'size': 10})

        self.fig.canvas.draw()

    def on_key_press(self, event):
        if event.key == 'shift':
            self.shift_is_held = True
        if event.key == 'u':
            self.u_is_held = True

    def on_key_release(self, event):
        if event.key == 'shift':
            self.shift_is_held = False
        if event.key == 'u':
            self.u_is_held = False
