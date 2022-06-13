# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 21:29:43 2016

@author: heinz
"""

import numpy as np

class SingleSpectrum:
    def __init__(self, wavelengths): 
        self.counts = np.zeros(len(wavelengths))
        self.wavelengths = wavelengths
        