# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 22:27:45 2016

@author: heinz
"""

import win32com.client as wc
import time

def initmono(force_reinit=False):
    wc.pythoncom.CoInitialize()
    mono = wc.Dispatch('JYMono.Monochromator')

    print(mono.GetComponentVersion())
    mono.Uniqueid = "Mono1" 
    mono.Load()
    mono.OpenCommunications()
    mono.Initialize(force_reinit,False)
    time.sleep(1)
    
    print(mono.FirmwareVersion)
    print(mono.Description)
    print(mono.Name)
    
    mono.MoveToSlitWidth(0,2.24)
    
    return mono
def mono_calibrate(mono, actual_wavelength) :
    mono.Calibrate(actual_wavelength)

def mono_getslitwidth(mono):
    return mono.GetCurrentSlitWidth(0)

def mono_setslitwidth(mono, slitwidth):
    mono.MoveToSlitWidth(0, slitwidth)
    
def mono_getgrating(mono):
    turret = mono.GetCurrentTurret()
    cur,rulings,blaze,index = mono.GetCurrentGratingWithDetails()
    return (rulings[turret],blaze[turret])

# turrets:
# 0 is grating "1" with 1200 g/mm, 500 nm blaze
# 1 is grating "2" 150 g/mm with 500 nm blaze,
# 2 is grating "3" with 150 g/mm, 1200 nm blaze
def mono_setgrating(mono, turret): 
    mono.MovetoTurret(turret)
    print('Moving turret')
    while True:
        time.sleep(0.5)
        if mono.IsBusy() == False:
            break
    ruling, blaze = mono_getgrating(mono)
    print('Moving complete; new grating: %r g/mm, %r blaze' % (ruling,blaze))

def mono_frontexit(mono):
    return (mono.GetCurrentMirrorPosition(1) == 2)
    
def mono_setfrontexit(mono,front_exit):
    print('Moving mirror')
    if front_exit:
        mono.MoveToMirrorPosition(1,2)
    else:
        mono.MoveToMirrorPosition(1,3)
    
    print('Moving complete; front exit is now %r' % (mono_frontexit(mono)))
    
    
def mono_getwavelength(mono):
    return mono.GetCurrentWavelength()
    
def mono_setwavelength(mono,wavelength):
    mono.MovetoWavelength(wavelength)
    print('Moving center wavelength')
    while True:
        time.sleep(0.2)
        if mono.IsBusy() == False:
            break
    print('Moving complete; new center wavelength: %r nm' % (mono_getwavelength(mono)))
