# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 22:21:47 2016

@author: heinz
"""

#%run 'ccd3000_visa.ipynb'
#%run 'mono.ipynb'
#%run 'synapse.ipynb'
#%run 'fileio.ipynb'
#%run 'spectra.ipynb'

import time
import signal
import numpy as np
import matplotlib.pyplot as plt
from IPython import display
import datetime
import pickle
import os
from fileio import *
from synapse import *
from ccd3000_visa import *
from spectra import SingleSpectrum
from mono import *


def acqsetup(using_synapse, det, mono, center, exposure, numavgs, ystart, yend):

    # set up hardware
    if using_synapse:
        ccd = det
        queryfn = querysynapse
        # spectrum mode on
        synapse_roi(det, 1, 1, ystart+1, 1024, yend-ystart+1, 1, yend-ystart+1) # ccd is 1-indexed
        synapse_exp(det, exposure)
        arraysize = 1024
        if mono_frontexit(mono) == False:
            mono_setfrontexit(mono,True)
        delta = 0.3
    else:
        ccd = det
        queryfn = queryccd3000_visa
        prepccd3000_visa(det, exposure)
        #ccd3000_exp(ccd3000, exposure)
        arraysize = 512
        if mono_frontexit(mono) == True:
            mono_setfrontexit(mono,False)
        delta = 0.572
        ystart = 1
        yend = 1
        
    # 1 nm tolerance on spectral center
    if abs(mono_getwavelength(mono)-center) > 1:
        mono_setwavelength(mono,center)
        time.sleep(5)
    center = mono_getwavelength(mono) # update to "true" center
    slitwidth = mono_getslitwidth(mono)
    grating = '%r g/mm, %s blaze' % mono_getgrating(mono)
    detector = getname(ccd)
    
    wavelengths = np.linspace(center-delta*arraysize/2,center+delta*arraysize/2,arraysize)
    
    spectrum = SingleSpectrum(wavelengths)
    
    return (ccd,spectrum,queryfn)


def acqsetup2(using_synapse, det, mono, center, exposure, numavgs, ystart, yend, slwdth):

    
    # set up hardware
    if using_synapse:
        ccd = det
        queryfn = querysynapse
        # spectrum mode on
        synapse_roi(det, 1, 1, ystart+1, 1024, yend-ystart+1, 1, yend-ystart+1) # ccd is 1-indexed
        synapse_exp(det, exposure)
        arraysize = 1024
        if mono_frontexit(mono) == False:
            mono_setfrontexit(mono,True)
        delta = 0.3
    else:
        ccd = det
        queryfn = queryccd3000_visa
        prepccd3000_visa(det, exposure)
        #ccd3000_exp(ccd3000, exposure)
        arraysize = 512
        if mono_frontexit(mono) == True:
            mono_setfrontexit(mono,False)
        delta = 0.572
        ystart = 1
        yend = 1
        
    # 1 nm tolerance on spectral center
    if abs(mono_getwavelength(mono)-center) > 1:
        mono_setwavelength(mono,center)
        time.sleep(5)
    center = mono_getwavelength(mono) # update to "true" center
    mono_setslitwidth(mono, slwdth)
    slitwidth = mono_getslitwidth(mono)
    grating = '%r g/mm, %s blaze' % mono_getgrating(mono)
    detector = getname(ccd)
    
    wavelengths = np.linspace(center-delta*arraysize/2,center+delta*arraysize/2,arraysize)
    
    spectrum = SingleSpectrum(wavelengths)
    
    return (ccd,spectrum,queryfn)


# xsize, ysize are scan window size in microns
# looks for globals mono, synapse, ccd3000; using_synapse=True runs with synapse, else runs with ccd3000. 
def acquire(using_synapse, det, mono, center, exposure, numavgs, 
             ystart, yend,spect_name, show_spect,slwdth):
#    %matplotlib inline

#    full_filename = makefilename(filename)
    
    (ccd,spectrum,queryfn) = acqsetup2(using_synapse, det, mono, center, exposure, numavgs, ystart, yend,slwdth)
    
    
    arraysize = len(spectrum.wavelengths)
    
    
    # current spectrum setup
#    fig = plt.figure(figsize=(10, 4)) 
#    fig.suptitle(full_filename, fontsize=15)
#    ax = plt.gca()
#    ax.set_xlabel('Wavelength (nm)', fontsize=14)
#    ax.set_ylabel('Counts', fontsize=14)
#    plt.show()
#    cur_min = 66000
#    cur_max = -66000
    
    #queryfn(ccd) # dummy call to ccd
            
    try:
        for n in range(numavgs):
            spectrum.counts += queryfn(ccd)

        spectrum.counts = spectrum.counts/numavgs

        # show average
        ydata = spectrum.counts
        if show_spect:
            fig=plt.figure()
            plt.plot(spectrum.wavelengths,spectrum.counts)
            plt.title(spect_name)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Counts')
            plt.show()
    except: # user is trying to exit. make sure no messages are waiting 
        raise
        
#    savedata(full_filename,spectrum)
    
    return spectrum


