# import pyqtgraph as pg
# from pyqtgraph.Qt import QtGui
# from pyqtgraph.dockarea import DockArea, Dock
# pg.setConfigOption('background', 'w') ## Switch to using white background and black foreground
# pg.setConfigOption('foreground', 'k')
# from PyQt5.QtWidgets import QApplication, QPushButton
# from PyQt5.QtCore import  QTimer

# class InspectionWindow(QtGui.QMainWindow):
#     def __init__(self, SimpleScan):
#         self.Experiment = SimpleScan
#         self.realTimeUpdate = False
#         super().__init__()

#         area = DockArea()
#         self.setCentralWidget(area)
#         self.setWindowTitle('Best Program Ever')

#         RTCDock = Dock("Real Time", size=(500,400))
#         area.addDock(RTCDock, 'left')

#         RTCWin = pg.LayoutWidget()
#         self.RTFigure = pg.GraphicsWindow()
#         self.RTPlot = self.RTFigure.addPlot()
#         button = QPushButton('Start RTC')
#         RTCWin.addWidget(button, 3, 0)
#         button.clicked.connect(self.start)

#         button = QPushButton('Stop RTC')
#         RTCWin.addWidget(button, 4, 0)
#         button.clicked.connect(self.stop)
#         RTCWin.addWidget(self.RTFigure, 5, 0, 5, 3)

#         RTCDock.addWidget(RTCWin)

#         for device in self.Experiment.scan_instruments:
#             device.generate_widget(area)

#         self.timer = QTimer()
#         self.timer.setInterval(40)
#         self.timer.timeout.connect(self.eventLoop)
#         self.timer.start()

#     def eventLoop(self):
#         if self.realTimeUpdate:
#             Is = self.Experiment.measurement_instrument.measure()


#             self.RTPlot.clear()
#             self.RTPlot.plot(Is, pen=pg.mkPen('b', width=2))

#     def start(self):
#         """
#         Enable scanning by setting the global flag to True.
#         Not in use currently.
#         """
#         self.realTimeUpdate = True

#     def stop(self):
#         """
#         Stop scanning by setting the global flag to False.
#         """
#         self.realTimeUpdate = False

#     def closeEvent(self, event):
#         '''
#         Leave this function here for smooth exiting.
#         Exit dialog is added to choose whether shuting down is necessary
#         '''
#         self.stop()
#         event.accept()
#         app = QApplication.instance()
#         app.quit()


# #%%
# if __name__=='__main__':
#     from LightWork.MeasurementObjects.TestMeasurementObject import TestMeasurementObject
#     from LightWork.ScanObjects.TestScanObject import TestScanObject
#     from LightWork.SimpleScan import SimpleScan
#     import numpy as np
#     import os
#     import sys

#     measurer = TestMeasurementObject()
#     scanner = TestScanObject(name='1', scan_values=np.arange(0, 10, 1), scan_nest_index=0)

#     Experiment = SimpleScan(
#         measurement_instrument=measurer, scan_instruments=[scanner], laser_shutter=False,
#         savepath=os.path.join(os.getcwd(), 'test'),
#         savename='test', save_npz=0, notify_me=False
#         )
#     if not QApplication.instance():
#         app = QApplication(sys.argv)
#     else:
#         app = QApplication.instance()
#     app.setStyle('Fusion')
#     MainWindow = InspectionWindow(Experiment)
#     MainWindow.show()
#     sys.exit(app.exec_())

import glob
import os
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph.dockarea import DockArea, Dock
# Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class InspectionWindow(QtGui.QMainWindow):
    def __init__(self):
        self.realTimeUpdate = False
        super().__init__()

        area = DockArea()
        self.setCentralWidget(area)
        self.setWindowTitle('Light Work')

        MeasurementDock = Dock("Measurement", size=(500, 400))
        area.addDock(MeasurementDock, 'left')

        MeasurementWin = pg.LayoutWidget()
        self.MeasurementFig = pg.GraphicsWindow()
        self.MeasurementPlot = self.MeasurementFig.addPlot()
        add_measurer_button = QPushButton('Add Measurement Object')
        MeasurementWin.addWidget(add_measurer_button, 0, 0)
        add_measurer_button.clicked.connect(self.add_measurer_object)

        button = QPushButton('Stop RTC')
        MeasurementWin.addWidget(button, 4, 0)
        button.clicked.connect(self.stop)
        MeasurementWin.addWidget(self.RTFigure, 5, 0, 5, 3)

        RTCDock.addWidget(MeasurementWin)

        self.timer = QTimer()
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.eventLoop)
        self.timer.start()

    def eventLoop(self):
        pass

    def all_classes_in_dir(self, dir):
        for file in glob.glob(os.path.join(dir, '*.py')):
            name =

    def add_measurement_object(self):
        self.adddata_dialog = QDialog()
        self.adddata_dialog.bpflakeimage_checkbox = QCheckBox(
            "Add Flakes to BP labelled data?")
        self.adddata_dialog.bpblankimage_checkbox = QCheckBox(
            "Add Blanks to BP labelled data?")
        self.adddata_dialog.wseflakeimage_checkbox = QCheckBox(
            "Add Flakes to WSe2 labelled data?")
        self.adddata_dialog.wseblankimage_checkbox = QCheckBox(
            "Add Blanks to WSe2 labelled data?")
        self.adddata_dialog.done = QPushButton('Done')
        self.adddata_dialog.done.clicked.connect(self.importFlakeTinderLikes)
        layout = QGridLayout()
        layout.addWidget(self.adddata_dialog.bpflakeimage_checkbox, 0, 0)
        layout.addWidget(self.adddata_dialog.bpblankimage_checkbox, 1, 0)
        layout.addWidget(self.adddata_dialog.wseflakeimage_checkbox, 2, 0)
        layout.addWidget(self.adddata_dialog.wseblankimage_checkbox, 3, 0)
        layout.addWidget(self.adddata_dialog.done, 4, 0)
        self.adddata_dialog.setLayout(layout)
        self.adddata_dialog.setMinimumSize(100, 100)
        self.adddata_dialog.setWindowTitle(
            "Do you want to add these to the labelled data set?")
        self.adddata_dialog.show()

    # def add_measurement_object(self):
    #     self.adddata_dialog = QDialog()
    #     self.adddata_dialog.bpflakeimage_checkbox = QCheckBox("Add Flakes to BP labelled data?")
    #     self.adddata_dialog.bpblankimage_checkbox = QCheckBox("Add Blanks to BP labelled data?")
    #     self.adddata_dialog.wseflakeimage_checkbox = QCheckBox("Add Flakes to WSe2 labelled data?")
    #     self.adddata_dialog.wseblankimage_checkbox = QCheckBox("Add Blanks to WSe2 labelled data?")
    #     self.adddata_dialog.done = QPushButton('Done')
    #     self.adddata_dialog.done.clicked.connect(self.importFlakeTinderLikes)
    #     layout = QGridLayout()
    #     layout.addWidget(self.adddata_dialog.bpflakeimage_checkbox, 0,0)
    #     layout.addWidget(self.adddata_dialog.bpblankimage_checkbox, 1,0)
    #     layout.addWidget(self.adddata_dialog.wseflakeimage_checkbox, 2,0)
    #     layout.addWidget(self.adddata_dialog.wseblankimage_checkbox, 3,0)
    #     layout.addWidget(self.adddata_dialog.done, 4,0 )
    #     self.adddata_dialog.setLayout(layout)
    #     self.adddata_dialog.setMinimumSize(100,100)
    #     self.adddata_dialog.setWindowTitle("Do you want to add these to the labelled data set?")
    #     self.adddata_dialog.show()

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


# %%
if __name__ == '__main__':
    import glob
    import LightWork.MeasurementObjects.TestMeasurementObject as t
    for file in glob(os.path.dirname(t.__file__)):
        name = os.path.splitext(os.path.basename(file))[0]
        module = __import__(name)
        for member in dir(module):
            print(module)
    # import sys
    # if not QApplication.instance():
    #     app = QApplication(sys.argv)
    # else:
    #     app = QApplication.instance()
    # app.setStyle('Fusion')
    # MainWindow = InspectionWindow()
    # MainWindow.show()
    # sys.exit(app.exec_())
