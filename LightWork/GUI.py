import glob
import os
import importlib
import LightWork.MeasurementObjects.TestMeasurementObject as m
import LightWork.ScanObjects.TestScanObject as s
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QLineEdit, QTabWidget, QGridLayout, QLabel, QWidget, QComboBox, QTableWidget, QTableWidgetItem
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
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
        
        self.experiment_objects = {}
        self.experiment_objects_combobox = QComboBox()
        self.experiment_objects_combobox.addItems(self.generate_all_possible_experiment_objects(fullname=True))
        self.experiment_objects_tab.layout.addWidget(self.experiment_objects_combobox, 0, 0, 1, 1)
            
        add_object_button = QPushButton('Add Experiment Object')
        add_object_button.clicked.connect(self.add_experiment_object)
        self.experiment_objects_tab.layout.addWidget(add_object_button, 0, 1, 1, 1)
        self.experiment_objects_tab.setLayout(self.experiment_objects_tab.layout)

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
    
    def generate_all_possible_experiment_objects(self, fullname=True):
        object_options = self.all_classes_in_dir(os.path.dirname(s.__file__))
        object_options.extend(self.all_classes_in_dir(os.path.dirname(m.__file__)))
        if fullname == False:
            object_options = [i.split('MeasurementObject')[0].split('ScanObject')[0]for i in object_options]
        return object_options

    def add_experiment_object(self):
        self.define_experiment_object_dialog = QDialog()
        object_to_add = self.experiment_objects_combobox.currentText()
        if 'Measurement' in object_to_add:
            experiment_object_class = getattr(importlib.import_module('.{}'.format(object_to_add), 'LightWork.MeasurementObjects'), '{}'.format(object_to_add))
        else:
            experiment_object_class = getattr(importlib.import_module('.{}'.format(object_to_add), 'LightWork.ScanObjects'), '{}'.format(object_to_add))
        sig = inspect.signature(experiment_object_class)
        # Create dictionary 
        arguments = {}
        for param in sig.parameters.values():
            if param.default is param.empty:
                arguments[param.name] = ''
            else:
                arguments[param.name] = param.default
                
        argument_table = QTableWidget()
        argument_table.setColumnCount(len(arguments.keys()))
        argument_table.setRowCount(1)
        for count, (key, value) in enumerate(arguments.items()):
            newitem = QTableWidgetItem(value)
            argument_table.setItem(0, count, newitem)
            argument_table.setHorizontalHeaderItem(count, QtGui.QTableWidgetItem(key))
        argument_table.setVerticalHeaderItem(0, QtGui.QTableWidgetItem(object_to_add))
        argument_table.resizeColumnsToContents()
        argument_table.resizeRowsToContents()
        
        self.define_experiment_object_dialog.verticalLayout = QtGui.QVBoxLayout(self.define_experiment_object_dialog)
        self.define_experiment_object_dialog.verticalLayout.addWidget(argument_table)
        self.define_experiment_object_dialog.buttonBox = QtGui.QDialogButtonBox(self.define_experiment_object_dialog)
        self.define_experiment_object_dialog.buttonBox.setOrientation(Qt.Horizontal)
        self.define_experiment_object_dialog.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.define_experiment_object_dialog.verticalLayout.addWidget(self.define_experiment_object_dialog.buttonBox)
        self.define_experiment_object_dialog.buttonBox.accepted.connect(lambda: self.save_experiment_object(argument_table))
        self.define_experiment_object_dialog.buttonBox.rejected.connect(self.define_experiment_object_dialog.close)
        self.define_experiment_object_dialog.setLayout(self.define_experiment_object_dialog.verticalLayout)
        self.define_experiment_object_dialog.setWindowTitle("Define parameters for {}".format(object_to_add))
        self.define_experiment_object_dialog.resize(200*len(arguments.keys()), 200)
        self.define_experiment_object_dialog.show()
    
    def save_experiment_object(self, argument_table):
        pass
        # args = argument_string.split(',')
        # bad_args = [elem[:-1] for elem in args if elem[-1] == '=']
        # # import pdb
        # # pdb.set_trace()
        # if bad_args:
        #     self.define_experiment_object_dialog.warning_label.setText('Please add values for: {}'.format(*bad_args))
        #     self.define_experiment_object_dialog.warning_label.setHidden(False)
        #     return
        # self.define_experiment_object_dialog.close()   

    

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
