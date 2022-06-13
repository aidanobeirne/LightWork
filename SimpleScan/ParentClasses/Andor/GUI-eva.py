# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 09:33:54 2021

@author: HeinzLab
"""

import re
import glob
import numpy as np
from numpy.lib import recfunctions as rfn
import copy
import sys
import os
import pylab as pl
import matplotlib.pyplot as plt


plt.close('all')
xmin = 350
xmax = 550

##########################################################################################################################
data = []
angles = []
intensities = []
for file in glob.glob('c:/Users/HeinzLab/Documents/Aidan/BP-Magnetic field/Angular dependence - 0T/converted/*.asc'):
#for file in glob.glob(r'C:\Users\HeinzLab\Documents\Aidan\BP-Magnetic field\-9T\converted\*.asc'):
    if '-90s' not in file:
        dat = np.genfromtxt(file, delimiter=',')
        angle = int(os.path.basename(file).replace('-retake', '').split('HWP')[1].split('.asc')[0])
        data.append(dat[:,1])
        angles.append(angle)
        intensities.append(np.sum(dat[:,1][xmin: xmax]))
        energies = 1240/dat[:,0]
        
#data = [x for _, x in sorted(zip(angles,data))]
#angles = sorted(angles)
colors = pl.cm.jet(np.linspace(0,1,len(angles)))

plt.figure()
for dat, angle, color in zip(data, angles, colors):
    plt.plot(energies, dat, color = color, label = angle)
plt.legend()
plt.title('0T')
plt.axvline(energies[xmin], color = 'red')
plt.axvline(energies[xmax], color = 'blue')
plt.figure()
plt.scatter(angles, intensities)
plt.title('0T')
##########################################################################################################################
# -9 T
data = []
angles = []
intensities = []
for file in glob.glob(r'C:\Users\HeinzLab\Documents\Aidan\BP-Magnetic field\-9T\original\*.asc'):
    if '-90s' not in file:  
        angle = float(os.path.basename(file).split('HWP')[1].split('.asc')[0])
        print(file, ' ', angle)
        dat = np.genfromtxt(file, delimiter=',')
        data.append(dat[:,1])
        angles.append(angle)
        intensities.append(np.sum(dat[:,1][xmin: xmax]))       
        energies = 1240/dat[:,0]
#data = [x for _ , x in sorted(zip(angles,data))]
#angles = sorted(angles)
colors = pl.cm.jet(np.linspace(0,1,len(angles)))

plt.figure()
for dat, angle, color in zip(data, angles, colors):
    plt.plot(energies, dat, color = color, label = angle)
plt.legend()
plt.title('-9T')
plt.axvline(energies[xmin], color = 'red')
plt.axvline(energies[xmax], color = 'blue')
plt.figure()
plt.scatter(angles, intensities)
plt.title('-9T')
##########################################################################################################################
#
#data = []
#angles = []
#intensities = []
#for file in glob.glob(r'C:\Users\HeinzLab\Documents\Aidan\BP-Magnetic field\-9T\updated\*.asc'):
#    dat = np.genfromtxt(file, delimiter=',')
#    angle = int(os.path.basename(file).replace('-retake','').split('HWP')[1].split('.asc')[0])
#    print(file, ' ', angle)
#    data.append(dat[:,1])
#    angles.append(angle)
#    intensities.append(np.sum(dat[:,1][xmin: xmax]))       
#    energies = 1240/dat[:,0]
##data = [x for _ , x in sorted(zip(angles,data))]
##angles = sorted(angles)
#colors = pl.cm.jet(np.linspace(0,1,len(angles)))
##
##for dat, angle, color in zip(data, angles, colors):
##    plt.plot(energies, dat, color = color, label = angle)
##plt.legend()
##plt.axvline(energies[xmin], color = 'red')
##plt.axvline(energies[xmax], color = 'blue')
#plt.figure()
#plt.scatter(angles, intensities)
##########################################################################################################################
# -7 T
data = []
angles = []
intensities = []
for file in glob.glob(r'C:\Users\HeinzLab\Documents\Aidan\BP-Magnetic field\-7T\converted\*.asc'): 
    angle = float(os.path.basename(file).split('HWP')[1].split('.asc')[0])
    print(file, ' ', angle)
    dat = np.genfromtxt(file, delimiter=',')
    data.append(dat[:,1])
    angles.append(angle)
    intensities.append(np.sum(dat[:,1][xmin: xmax]))       
    energies = 1240/dat[:,0]
#data = [x for _,x in sorted(zip(angles,data))]
#angles = sorted(angles)
colors = pl.cm.jet(np.linspace(0,1,len(angles)))

plt.figure()
for dat, angle, color in zip(data, angles, colors):
    plt.plot(energies, dat, color = color, label = angle)
plt.legend()
plt.title('-7T')
plt.axvline(energies[xmin], color = 'red')
plt.axvline(energies[xmax], color = 'blue')
plt.figure()
plt.scatter(angles, intensities)
plt.title('-7T')
##########################################################################################################################
# -7 T wide slit
#data = []
#angles = []
#intensities = []
#for file in glob.glob(r'C:\Users\HeinzLab\Documents\Aidan\BP-Magnetic field\-7T_slitopen\converted\*.asc'): 
#    angle = float(os.path.basename(file).split('HWP')[1].split('.asc')[0])
#    print(file, ' ', angle)
#    dat = np.genfromtxt(file, delimiter=',')
#    data.append(dat[:,1])
#    angles.append(angle)
#    intensities.append(np.sum(dat[:,1][xmin: xmax]))       
#    energies = 1240/dat[:,0]
##data = [x for _,x in sorted(zip(angles,data))]
##angles = sorted(angles)
#colors = pl.cm.jet(np.linspace(0,1,len(angles)))
#
#plt.figure()
#for dat, angle, color in zip(data, angles, colors):
#    plt.plot(energies, dat, color = color, label = angle)
#plt.legend()
#plt.title('-7T 300 um slit')
#plt.axvline(energies[xmin], color = 'red')
#plt.axvline(energies[xmax], color = 'blue')
#plt.figure()
#plt.scatter(angles, intensities)
#plt.title('-7T 300 um slit')
##########################################################################################################################
# -5 T
data = []
angles = []
intensities = []
for file in glob.glob(r'C:\Users\HeinzLab\Documents\Aidan\BP-Magnetic field\-5T\converted\*.asc'): 
    angle = float(os.path.basename(file).split('HWP')[1].split('.asc')[0])
    print(file, ' ', angle)
    dat = np.genfromtxt(file, delimiter=',')
    data.append(dat[:,1])
    angles.append(angle)
    intensities.append(np.sum(dat[:,1][xmin: xmax]))       
    energies = 1240/dat[:,0]
#data = [x for _,x in sorted(zip(angles,data))]
#angles = sorted(angles)
colors = pl.cm.jet(np.linspace(0,1,len(angles)))

plt.figure()
for dat, angle, color in zip(data, angles, colors):
    plt.plot(energies, dat, color = color, label = angle)
plt.legend()
plt.title('-5T')
plt.axvline(energies[xmin], color = 'red')
plt.axvline(energies[xmax], color = 'blue')
plt.figure()
plt.scatter(angles, intensities)
plt.title('-5T')
##########################################################################################################################
# -3 T
data = []
angles = []
intensities = []
for file in glob.glob(r'C:\Users\HeinzLab\Documents\Aidan\BP-Magnetic field\-3T\converted\*.asc'): 
    angle = float(os.path.basename(file).split('HWP')[1].split('.asc')[0])
    print(file, ' ', angle)
    dat = np.genfromtxt(file, delimiter=',')
    data.append(dat[:,1])
    angles.append(angle)
    intensities.append(np.sum(dat[:,1][xmin: xmax]))       
    energies = 1240/dat[:,0]
#data = [x for _,x in sorted(zip(angles,data))]
#angles = sorted(angles)
colors = pl.cm.jet(np.linspace(0,1,len(angles)))

plt.figure()
for dat, angle, color in zip(data, angles, colors):
    plt.plot(energies, dat, color = color, label = angle)
plt.legend()
plt.title('-3T')
plt.axvline(energies[xmin], color = 'red')
plt.axvline(energies[xmax], color = 'blue')
plt.figure()
plt.scatter(angles, intensities)
plt.title('-3T')
##########################################################################################################################
# -1 T
data = []
angles = []
intensities = []
for file in glob.glob(r'C:\Users\HeinzLab\Documents\Aidan\BP-Magnetic field\-1T\converted\*.asc'): 
    angle = float(os.path.basename(file).split('HWP')[1].split('.asc')[0])
    print(file, ' ', angle)
    dat = np.genfromtxt(file, delimiter=',')
    data.append(dat[:,1])
    angles.append(angle)
    intensities.append(np.sum(dat[:,1][xmin: xmax]))       
    energies = 1240/dat[:,0]
#data = [x for _,x in sorted(zip(angles,data))]
#angles = sorted(angles)
colors = pl.cm.jet(np.linspace(0,1,len(angles)))

plt.figure()
for dat, angle, color in zip(data, angles, colors):
    plt.plot(energies, dat, color = color, label = angle)
plt.legend()
plt.title('-1T')
plt.axvline(energies[xmin], color = 'red')
plt.axvline(energies[xmax], color = 'blue')
plt.figure()
plt.scatter(angles, intensities)
plt.title('-1T')