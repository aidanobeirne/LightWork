import glob
import os
import LightWork.MeasurementObjects.TestMeasurementObject as m
import LightWork.ScanObjects.TestScanObject as s
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QLineEdit, QCheckBox, QTabWidget, QGridLayout, QLabel, QWidget, QWizard, QWizardPage
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph.dockarea import DockArea, Dock
import inspect
# Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class InspectionWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.setWindowTitle('Light Work')

        # Create the 3 main tabs
        self.experiment_objects_tab = QWidget()
        self.experiment_objects_tab.layout = QGridLayout()
        self.tabWidget.addTab(self.experiment_objects_tab,
                              "Experiment Objects")
        self.RTC_tab = QWidget()
        self.RTC_tab.layout = QGridLayout()
        self.tabWidget.addTab(self.RTC_tab, "RTC")
        self.scan_tab = QWidget()
        self.scan_tab.layout = QGridLayout()
        self.tabWidget.addTab(self.scan_tab, "Scan")

        add_object_button = QPushButton('Add Experiment Objects')
        add_object_button.clicked.connect(self.add_experiment_objects)
        self.experiment_objects_tab.layout.addWidget(add_object_button, 1, 1)
        self.experiment_objects_tab.setLayout(
            self.experiment_objects_tab.layout)

        # ObjectDock = Dock("Experiment Objects")

        # MeasurementDock = Dock("Measurement", size=(500, 400))
        # area.addDock(MeasurementDock, 'left')

        # MeasurementWin = pg.LayoutWidget()
        # self.MeasurementFig = pg.GraphicsWindow()
        # self.MeasurementPlot = self.MeasurementFig.addPlot()

        self.timer = QTimer()
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.eventLoop)
        self.timer.start()

    def eventLoop(self):
        pass

    def all_classes_in_dir(self, dir):
        names = []
        for file in glob.glob(os.path.join(dir, '*.py')):
            name = os.path.splitext(os.path.basename(file))[0]
            if 'init' in name:
                continue
            names.append(name)
        return names

    def add_experiment_objects(self):
        object_options = self.all_classes_in_dir(os.path.dirname(s.__file__))
        object_options.extend(self.all_classes_in_dir(os.path.dirname(m.__file__)))
        self.add_experiment_objects_dialog = QDialog()
        onlyInt = QtGui.QIntValidator()
        layout = QGridLayout()
        layout.addWidget(QLabel('Experiment Object'), 0,0)
        layout.addWidget(QLabel('Number to add'), 0,1)
        self.object_inputs = {}
        for count, experiment_object in enumerate(object_options):
            inputlabel = experiment_object.split('MeasurementObject')[0].split('ScanObject')[0]
            if 'Measurement' in experiment_object:
                self.object_inputs[experiment_object] = QCheckBox()
                self.object_inputs[experiment_object].stateChanged.connect((lambda experiment_object: lambda: self.uncheck_except(experiment_object))(experiment_object))
            else:
                self.object_inputs[experiment_object] = QLineEdit()
                self.object_inputs[experiment_object].setText('0')
                self.object_inputs[experiment_object].setValidator(onlyInt)
            layout.addWidget(QLabel(inputlabel), count+1, 0)
            layout.addWidget(self.object_inputs[experiment_object], count+1, 1)

        next_btn = QPushButton('done')
        layout.addWidget(next_btn, count+1, 0, 1, 2)
        next_btn.clicked.connect(self.define_experiment_objects_dialog)
        self.add_experiment_objects_dialog.setLayout(layout)
        self.add_experiment_objects_dialog.setMinimumSize(100,100)
        self.add_experiment_objects_dialog.setWindowTitle("Add Experiment objects")
        self.add_experiment_objects_dialog.show()
    
    def define_experiment_objects_dialog(self):
        self.add_experiment_objects_dialog.close()
        self.define_experiment_objects_dialog = QDialog()
        objects_to_add = []
        for key, value in self.object_inputs.items():
            if 'Measurement' in key:
                if value.isChecked():
                    objects_to_add.append(key)

            else:
                if int(value.text()) > 0:
                    for i in range(int(value.text())):
                        objects_to_add.append(key)
    
        layout = QGridLayout()
        print(objects_to_add)
        for count, key in enumerate(objects_to_add):
            if 'Measurement' in key:
                a = __import__('LightWork.MeasurementObjects.{}'.format(key))
            else:
                a = __import__('LightWork.ScanObjects.{}'.format(key))
            params = inspect.getfullargspec(a.__init__)[0]
            defaults = inspect.getfullargspec(a.__init__)[3]
            layout.addWidget(QLabel('{}'.format(key)), 2*count, 0, 2, 1)
            print(params, defaults)
            try:
                for i, (default,param) in enumerate(zip(defaults, params)):
                    layout.addWidget(QLabel(param), i+1, 2*count)
                    entry = QLineEdit()
                    entry.setText(str(default))
                    layout.addWidget(entry, i+1, 2*count+1)
            except TypeError:
                print(key)

        done_btn = QPushButton('done')
        layout.addWidget(done_btn, 2*count+1, 0, 1, 2)
        done_btn.clicked.connect(self.define_experiment_objects)
        self.define_experiment_objects_dialog.setLayout(layout)
        self.define_experiment_objects_dialog.setWindowTitle("Define Experiment objects")
        self.define_experiment_objects_dialog.show()

    # def add_experiment_objects(self):
    #     page1 = QWizardPage()
    #     page1.setWindowTitle('Add Experiment Objects')
    #     object_options = self.all_classes_in_dir(os.path.dirname(s.__file__))
    #     object_options.extend(self.all_classes_in_dir(
    #         os.path.dirname(m.__file__)))
    #     onlyInt = QtGui.QIntValidator()
    #     page1layout = QGridLayout()
    #     page1layout.addWidget(QLabel('Experiment Object'), 0, 0)
    #     page1layout.addWidget(QLabel('Number to add'), 0, 1)
    #     self.object_inputs = {}
    #     for count, experiment_object in enumerate(object_options):
    #         inputlabel = experiment_object.split('MeasurementObject')[0].split('ScanObject')[0]
    #         if 'Measurement' in experiment_object:
    #             self.object_inputs[experiment_object] = QCheckBox()
    #             self.object_inputs[experiment_object].stateChanged.connect(
    #                 (lambda experiment_object: lambda: self.uncheck_except(experiment_object))(experiment_object))
    #         else:
    #             self.object_inputs[experiment_object] = QLineEdit()
    #             self.object_inputs[experiment_object].setText('0')
    #             self.object_inputs[experiment_object].setValidator(onlyInt)
    #         page1layout.addWidget(QLabel(inputlabel), count+1, 0)
    #         page1layout.addWidget(
    #             self.object_inputs[experiment_object], count+1, 1)
    #     page1.setLayout(page1layout)

    #     self.page2 = QWizardPage()
    #     self.page2.setWindowTitle('Define Experiment Object parameters')
        
        
    #     self.wizard = QWizard()
    #     self.wizard.addPage(page1)
    #     self.wizard.addPage(self.page2)
    #     self.wizard.currentIdChanged.connect(lambda : self.build_page2_layout())

    #     self.wizard.show()
        
    
    # def build_page2_layout(self):
    #     print('next clicked')
    #     objects_to_add = []
    #     for key, value in self.object_inputs.items():

    #         if 'Measurement' in key:
    #             if value.isChecked():
    #                 objects_to_add.append(key)

    #         else:
    #             if int(value.text()) > 0:
    #                 for i in range(int(value.text())):
    #                     objects_to_add.append(key)

                        
    #     page2layout = QGridLayout()
    #     print(objects_to_add)
    #     for count, key in enumerate(objects_to_add):
    #         bare_label = key.split('MeasurementObject')[0].split('ScanObject')[0]
    #         if 'Measurement' in key:
    #             a = __import__('LightWork.MeasurementObjects.{}'.format(key))
    #         else:
    #             a = __import__('LightWork.ScanObjects.{}'.format(key))
    #         params = inspect.getfullargspec(a.__init__)[0]
    #         defaults = inspect.getfullargspec(a.__init__)[3]
    #         page2layout.addWidget(QLabel('{}'.format(bare_label)), 2*count, 0, 2, 1)
    #         try:
    #             for i, (default,param) in enumerate(zip(defaults, params)):
    #                 page2layout.addWidget(QLabel(param), i+1, 2*count)
    #                 page2layout.addWidget(QLineEdit(default), i+1, 2*count+1)
    #         except TypeError:
    #             print(key)
    #     self.page2.addLayout(page2layout)
                
    def uncheck_except(self, key_to_keep_checked):
        for key, value in self.object_inputs.items():
            if 'Measurement' in key:
                if key in key_to_keep_checked:
                    pass
                else:
                    value.blockSignals(True)
                    value.setChecked(False)
                    value.blockSignals(False)

    def define_experiment_objects(self):
        pass
        # for key, value in self.object_inputs.items():

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


if __name__ == '__main__':
    import sys

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    app.setStyle('Fusion')
    MainWindow = InspectionWindow()
    MainWindow.show()
    sys.exit(app.exec_())
# %%
