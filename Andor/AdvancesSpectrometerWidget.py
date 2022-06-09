# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 17:34:24 2020

@author: GloveBox
"""


# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:37:53 2020

@author: marku
"""

import platform
from ctypes import *
from PIL import Image
import sys

import time
import threading
import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import qApp, QCheckBox, QFileDialog, QSpinBox, QSlider, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QGroupBox, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QLineEdit, QDoubleSpinBox, QPlainTextEdit
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QVector3D, QIcon
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QRect, QPoint
from PyQt5 import QtCore


class AdvancedSpectrometerWidget(QWidget):
    def closeEvent(self, event):
        print("Shutting down Spectrometer")    
        print(self.SpecDll.ShamrockClose())
        for CamNumber in range(self.HowManyCams.value):
            print('Shutting down Camera '+str(CamNumber+1))
            self.CamDLL.SetCurrentCamera(self.CameraHandles[CamNumber])
            self.CamDLL.ShutDown()      
        print("Both cameras shut down.")
        
        event.accept()
        app.quit()
    
    def __init__(self):      
        super().__init__()
        basic_layout = QGridLayout()
        self.setLayout(basic_layout)
        
        self.SpectrometerGroupBox = QGroupBox("Spectrometer")
        layout = QGridLayout()
        
        self.CamDLL = WinDLL(r"C:\Users\GloveBox\Documents\Python Scripts\Andor\atmcd64d.dll")
        self.SpecDll = WinDLL(r"C:\Users\GloveBox\Documents\Python Scripts\Andor\atspectrograph.dll")
        
        self.HowManyCams = c_long()
        self.CamDLL.GetAvailableCameras(byref(self.HowManyCams))
        print('Found '+str(self.HowManyCams.value)+' Cameras')
        self.CameraHandles = []
        
        self.CameraComboBox = QComboBox()
    
        print('Starting Cameras')
        for CamNumber in range(self.HowManyCams.value):
            Handle = c_long()
            self.CamDLL.GetCameraHandle(c_long(CamNumber),byref(Handle))
            self.CameraHandles.append(Handle)
            
            print('Starting Camera '+str(CamNumber+1))
            self.CamDLL.SetCurrentCamera(self.CameraHandles[CamNumber])
            tekst = c_char()  
            error = self.CamDLL.Initialize(byref(tekst))
            
            
            
            serial = c_int()
            self.CamDLL.GetCameraSerialNumber(byref(serial))
            print("Camera has serial number: "+str(serial.value))
            
            # 24942 = InGaAs
            
            cw = c_int()
            ch = c_int()
            self.CamDLL.GetDetector(byref(cw), byref(ch))
            print("Camera has dimensions: " + str(cw.value) +" x " + str(ch.value))
            Number = CamNumber
            self.CameraComboBox.addItem("Cam #"+str(serial.value)+ " ["+str(cw.value) + "x" + str(ch.value)+ "]",Number)
            
            
        print("Cameras started")
        self.CameraComboBox.setCurrentIndex(self.HowManyCams.value-1)
        layout.addWidget(self.CameraComboBox, 0, 0, 1, 3)
        self.CameraComboBox.currentIndexChanged.connect(self.ChangeCamera)
        
        
        
        print("Starting spectrometer")
        tekst = c_char()        
        error = self.SpecDll.ShamrockInitialize(byref(tekst))
        print("Spectrometer started")
        
        Num = c_int()
        print(self.SpecDll.ShamrockGetNumberDevices(byref(Num)))
        print("Found " + str(Num.value) + " spectrometer")
        
        self.wl_calibration = []
        self.current_shamrock = 0
        
        btn = QPushButton("Take Spectrum")
        btn.clicked.connect(self.takeSpectrum)
        layout.addWidget(btn, 1, 0, 1, 3)
        
        #===============================
        
        layout.addWidget(QLabel("Temperature: "), 2, 0)
        self.TemperatureSpinBox = QSpinBox()
        self.TemperatureSpinBox.setRange(-95, 25)
        self.TemperatureSpinBox.setValue(-70)
        layout.addWidget(self.TemperatureSpinBox, 2, 1)
        
        btn = QPushButton("Set")
        btn.clicked.connect(self.setTemperature)
        layout.addWidget(btn, 2, 2)
        
        
        layout.addWidget(QLabel("Exposure time: "), 3, 0)
        self.ExposureSpinBox = QDoubleSpinBox()
        self.ExposureSpinBox.setRange(0, 1000)
        self.ExposureSpinBox.setValue(0.1)
        layout.addWidget(self.ExposureSpinBox, 3, 1)
        btn = QPushButton("Set")
        btn.clicked.connect(self.SetExposureTime)
        layout.addWidget(btn, 3, 2)
        
        self.coolerCheckbox = QCheckBox('Cooler')
        self.coolerCheckbox.stateChanged.connect(self.toggleCooler)
        layout.addWidget(self.coolerCheckbox, 4, 0, 1, 1)
        
        self.StatusLabel = QLabel("--")
        layout.addWidget(self.StatusLabel, 4, 1, 1, 1)
        
        btn = QPushButton("Update")
        btn.clicked.connect(self.updateParameters)
        layout.addWidget(btn, 4, 2, 1, 1)
        
        layout.addWidget(QLabel("Wavelength: "), 5, 0)
        self.WavelengthSpinBox = QDoubleSpinBox()
        self.WavelengthSpinBox.setRange(0, 10000)
        layout.addWidget(self.WavelengthSpinBox, 5, 1)
        
        btn = QPushButton("Set")
        btn.clicked.connect(self.SetWavelength)
        layout.addWidget(btn, 5, 2)
        
        layout.addWidget(QLabel("Shutter: "), 6, 0)
        self.ShutterComboBox = QComboBox()
        self.ShutterComboBox.addItem("Closed",0)
        self.ShutterComboBox.addItem("Opened",1)
        self.ShutterComboBox.addItem("External",2)
        layout.addWidget(self.ShutterComboBox, 6, 1)
        
        btn = QPushButton("Set")
        btn.clicked.connect(self.SetShutter)
        layout.addWidget(btn, 6, 2)
        
        layout.addWidget(QLabel("Port: "), 7, 0)
        self.PortComboBox = QComboBox()
        self.PortComboBox.addItem("1",0)
        self.PortComboBox.addItem("2",1)
        
        layout.addWidget(self.PortComboBox, 7, 1)
        
        btn = QPushButton("Set")
        btn.clicked.connect(self.SetPort)
        layout.addWidget(btn, 7, 2)
        
        
        layout.addWidget(QLabel("Slit: "), 8, 0)
        self.SlitSpinBox = QDoubleSpinBox()
        self.SlitSpinBox.setRange(0, 1000)
        self.SlitSpinBox.setValue(0.1)
        layout.addWidget(self.SlitSpinBox, 8, 1)
        btn = QPushButton("Set")
        btn.clicked.connect(self.SetSlit)
        layout.addWidget(btn, 8, 2)
        
        layout.addWidget(QLabel("Grating: "), 9, 0)
        self.GratingComboBox = QComboBox()
        self.GratingComboBox.addItem("1",1)
        self.GratingComboBox.addItem("2",2)
        self.GratingComboBox.addItem("3",3)
        self.GratingComboBox.addItem("4",4)
        layout.addWidget(self.GratingComboBox, 9, 1)
        
        btn = QPushButton("Set")
        btn.clicked.connect(self.SetGrating)
        layout.addWidget(btn, 9, 2)
        
        #===============================
        self.ThreadLock = threading.Lock()
        
        self.SpectrometerGroupBox.setLayout(layout)
        basic_layout.addWidget(self.SpectrometerGroupBox,  0,0)
        print('0')
        self.updateParameters()
        self.WavelengthSpinBox.setValue(self.getWavelength())
        print('00')
 
    def updateParameters(self):
        print("1")
        exposure   = c_float()
        accumulate = c_float()
        kinetic    = c_float()
        error = self.CamDLL.GetAcquisitionTimings(byref(exposure),byref(accumulate),byref(kinetic))
        self.ExposureSpinBox.setValue(exposure.value)
        
        print("2")
        ctemperature = c_int()
        error = self.CamDLL.GetTemperature(byref(ctemperature))
        # self.TemperatureSpinBox.setValue(int(ctemperature.value))
        self.StatusLabel.setText("Temp: "+str(ctemperature.value))
        print("3")
        iCoolerStatus = c_int()
        error = self.CamDLL.IsCoolerOn(byref(iCoolerStatus))
        self.coolerCheckbox.stateChanged.disconnect()
        if iCoolerStatus.value != 0:
            self.coolerCheckbox.setChecked(True)
        else:
            self.coolerCheckbox.setChecked(False)
        print("4")
        self.coolerCheckbox.stateChanged.connect(self.toggleCooler)
        print("5")
        
        self.getWavelength()
        
        grating = c_int()
        error = self.SpecDll.ShamrockGetGrating(self.current_shamrock,byref(grating))
        self.GratingComboBox.setCurrentIndex(grating.value-1)


        shutter = c_int()
        error = self.SpecDll.ShamrockGetShutter(self.current_shamrock,byref(shutter))
        self.ShutterComboBox.setCurrentIndex(shutter.value)
        
        
        port = c_int()
        error = self.SpecDll.ShamrockGetPort(self.current_shamrock,byref(port))
        self.PortComboBox.setCurrentIndex(port.value)

        slit = c_float()
        error = self.SpecDll.ShamrockGetSlit(self.current_shamrock,byref(slit))
        self.SlitSpinBox.setValue(slit.value)




        
        
      
    def SetSlit(self):
        error = self.SpecDll.ShamrockSetSlit(self.current_shamrock,c_float(self.SlitSpinBox.value()))
    
    def SetPort(self):
        error = self.SpecDll.ShamrockSetPort(self.current_shamrock,c_int(self.PortComboBox.currentIndex()))

    
    def SetShutter(self):
        error = self.SpecDll.ShamrockSetShutter(self.current_shamrock,c_int(self.ShutterComboBox.currentIndex()))
    
    def SetGrating(self):
        error = self.SpecDll.ShamrockSetGrating(self.current_shamrock,c_int(self.GratingComboBox.currentIndex()+1))
       


        
    def ChangeCamera(self,index):
        self.CamDLL.SetCurrentCamera(self.CameraHandles[index])
        self.updateParameters()
    
    def setTemperature(self):
        self.CamDLL.SetTemperature(c_int(self.TemperatureSpinBox.value()))
        
    def SetExposureTime(self):
        self.CamDLL.SetExposureTime(c_float(self.ExposureSpinBox.value()))


    def getWavelength(self):
        curr_wave = c_float()
        error = self.SpecDll.ShamrockGetWavelength(self.current_shamrock,byref(curr_wave))
        
        numpix = c_int()
        cw = c_int()
        ch = c_int()
        self.CamDLL.GetDetector(byref(cw), byref(ch))
        print("Camera has dimensions: " + str(cw.value) +" x " + str(ch.value))
        
        numpix = cw
        
        print("px num:" + str(numpix.value))
        
        error = self.SpecDll.ShamrockSetNumberPixels(self.current_shamrock,numpix)

        fx_size = c_float()
        fy_size = c_float()
        self.CamDLL.GetPixelSize(byref(fx_size), byref(fy_size))
        print("px size: "+ str(fx_size.value))
        error = self.SpecDll.ShamrockSetPixelWidth(self.current_shamrock,fx_size)
        
        
        pixelw = c_float()
        error = self.SpecDll.ShamrockGetPixelWidth(self.current_shamrock,byref(pixelw))
        print("Px width:" + str(pixelw.value) )
        
        
        ccalib = c_float*numpix.value
        ccalib_array = ccalib()
        print(self.SpecDll.ShamrockGetCalibration(self.current_shamrock,pointer(ccalib_array),numpix))
        calib = []        
        
        for i in range(len(ccalib_array)):
            calib.append(ccalib_array[i])

        self.wl_calibration = calib[:]
        # print(self.wl_calibration)
        
        return curr_wave.value
    
    def SetWavelength(self):
        error = self.SpecDll.ShamrockSetWavelength(self.current_shamrock,c_float(self.WavelengthSpinBox.value()))
        self.WavelengthSpinBox.setValue(self.getWavelength())
    
    def threadingFunction(self):
        while self.ThreadRunning:
             
            self.ThreadLock.acquire()
            self.StatusLabel1.setText("Status: "+self.CamDLL.GetTemperature()+" Temp: "+str(self.CamDLL.temperature))
            if self.CamDLL.IsCoolerOn():
                self.StatusLabel2.setText("Cooler: ON")
            else:
                self.StatusLabel2.setText("Cooler: OFF")
            self.ThreadLock.release()
            
            if self.ContinousModeEnabledCheckbox.isChecked():
                self.ContinousMode = True
                self.LatestContinousSpectrum = self.takeSpectrum()
            else:
                self.ContinousMode = False
                time.sleep(1) 
        
    def toggleCooler(self):
        print("c1")
        self.ThreadLock.acquire()
        iCoolerStatus = c_int()
        error = self.CamDLL.IsCoolerOn(byref(iCoolerStatus))
        print("c2")
        if iCoolerStatus.value != 0:
            self.CamDLL.CoolerOFF()
           # I am a little afraid of turning off the cooler, since I read on a different documentation, 
           # taht one can only turn of the Cooler,when the temperature is up to -20 deg C...
           # self.CamDLL.CoolerOFF()
           # self.StatusLabel2.setText("Cooler: OFF")
        else:
           self.CamDLL.CoolerON()
        self.ThreadLock.release()
   
    def takeSpectrum(self):
        self.ThreadLock.acquire()
        error = self.CamDLL.StartAcquisition()
        self.CamDLL.WaitForAcquisition()
        cw = c_int()
        ch = c_int()
        self.CamDLL.GetDetector(byref(cw), byref(ch))
        dim = int(cw.value*ch.value)
        
        cimageArray = c_int * dim
        cimage = cimageArray()
        error = self.CamDLL.GetAcquiredData(pointer(cimage),dim)
        
        
        
        self.ThreadLock.release()
        data = []
        for i in range(len(cimage)):
            data.append(cimage[i])


        data = np.reshape(np.array(data[:]), (cw.value, ch.value) ) 
        

        # if self.BackgroundEnabledCheckbox.isChecked():
        #     data = data - self.Background
        
        if ch.value > 1:
            pg.plot(self.wl_calibration,np.sum(data,1))
        else:
            pg.plot(self.wl_calibration,data[:,0])
        return data
     
    def takeBackground(self):
        self.ThreadLock.acquire()
        error = self.CamDLL.StartAcquisition()
        self.CamDLL.WaitForAcquisition()
        data = []
        self.cam.GetAcquiredData(data)
        self.ThreadLock.release()
        self.Background = np.array(data)
        
if __name__ == '__main__':
    
    app = QApplication([])
    
    MainWindow = AdvancedSpectrometerWidget()
    MainWindow.show()
    sys.exit(app.exec_())