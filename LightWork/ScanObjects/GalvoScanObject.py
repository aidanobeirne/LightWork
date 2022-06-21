import time
import numpy as np
import sys
import os
from itertools import product
import nidaqmx as daq


class GalvoScanObject(object):
    def __init__(self, xmin, xmax, ymin, ymax, step, name='Galvo', scan_nest_index=0, conv=0.8/0.005):
        """

        Parameters
        ----------
        scan_nest_index : INT, optional
            THE INDEX OF THIS INSTRUMENT IN THE SCAN PROCEDURE. 0 CORRESPONDS TO AN INSTRUMENT WHOSE VALUES ARE CHANGED ONLY ONCE, 1 CORRESPONDS
            TO AN INSTRUMENT WHOSE VALUES ARE CHANGED TWICE, ETC. The default is 0.

        Returns
        -------
        None.

        """
        self.meta_data = {}
        self.conv = conv
        xarr = np.arange(xmin, xmax+step, step)
        yarr = np.arange(ymin, ymax+step, step)
        self.scan_values = list(product(xarr, yarr))
        self.scan_nest_index = scan_nest_index
        self.scan_instrument_name = name
        self.xdaq = daq.Task()
        self.ydaq = daq.Task()
        self.xdaq.ao_channels.add_ao_voltage_chan(b'Dev1/ao0')
        self.ydaq.ao_channels.add_ao_voltage_chan(b'Dev1/ao1')

    def set_scan_value(self, value):
        self.xdaq.write(value[0]/self.conv)
        self.ydaq.write(value[1]/self.conv)

    def get_save_data(self, value=None):
        data = {'x(um)': value[0],
                'y(um)': value[1]}
        print("coordinate:" + str(value))
        return data

    def get_scan_value(self):
        xpos = self.xdaq.read()/self.conv
        ypos = self.ydaq.read()/self.conv
        return 'um', xpos, ypos

    def close(self):
        self.xdaq.write(0)
        self.ydaq.write(0)
