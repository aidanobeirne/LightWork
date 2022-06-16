import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph.dockarea import DockArea, Dock
pg.setConfigOption('background', 'w') ## Switch to using white background and black foreground
pg.setConfigOption('foreground', 'k')
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtCore import  QTimer

class InspectionWindow(QtGui.QMainWindow):
    def __init__(self, SimpleScan): 
        self.Experiment = SimpleScan
        self.realTimeUpdate = False
        super().__init__()
        
        area = DockArea()
        self.setCentralWidget(area)
        self.setWindowTitle('Best Program Ever')
        
        RTCDock = Dock("Real Time", size=(500,400))
        area.addDock(RTCDock, 'left')
        
        RTCWin = pg.LayoutWidget()
        self.RTFigure = pg.GraphicsWindow()
        self.RTPlot = self.RTFigure.addPlot()
        button = QPushButton('Start RTC')
        RTCWin.addWidget(button, 3, 0)
        button.clicked.connect(self.start)
        
        button = QPushButton('Stop RTC')
        RTCWin.addWidget(button, 4, 0)
        button.clicked.connect(self.stop)
        RTCWin.addWidget(self.RTFigure, 5, 0, 5, 3)
        
        RTCDock.addWidget(RTCWin)
        
        for device in self.Experiment.scan_instruments:
            device.generate_widget(area)
        
        self.timer = QTimer()
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.eventLoop)
        self.timer.start()

    def eventLoop(self):
        if self.realTimeUpdate:
            Is = self.Experiment.measurement_instrument.measure()

            
            self.RTPlot.clear()
            self.RTPlot.plot(Is, pen=pg.mkPen('b', width=2))

    def start(self):
        """
        Enable scanning by setting the global flag to True.
        Not in use currently.
        """
        self.realTimeUpdate = True

    def stop(self):
        """
        Stop scanning by setting the global flag to False.
        """
        self.realTimeUpdate = False

    def closeEvent(self, event):
        '''
        Leave this function here for smooth exiting.
        Exit dialog is added to choose whether shuting down is necessary
        '''
        self.stop()
        event.accept()
        app = QApplication.instance()
        app.quit()


#%%
if __name__=='__main__':
    from LightWork.MeasurementObjects.TestMeasurementObject import TestMeasurementObject
    from LightWork.ScanObjects.TestScanObject import TestScanObject
    from LightWork.SimpleScan import SimpleScan
    import numpy as np
    import os
    import sys

    measurer = TestMeasurementObject()
    scanner = TestScanObject(name='1', scan_values=np.arange(0, 10, 1), scan_nest_index=0)
    
    Experiment = SimpleScan(
        measurement_instrument=measurer, scan_instruments=[scanner], laser_shutter=False,
        savepath=os.path.join(os.getcwd(), 'test'),
        savename='test', save_npz=0, notify_me=False
        )
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    app.setStyle('Fusion')
    MainWindow = InspectionWindow(Experiment)
    MainWindow.show()
    sys.exit(app.exec_())