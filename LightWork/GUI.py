import glob
import numpy as np
import os
import importlib
import LightWork.MeasurementObjects.TestMeasurementObject as m
import LightWork.ScanObjects.TestScanObject as s
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QTabWidget, QGridLayout, QWidget, QComboBox, QTableWidget, QTableWidgetItem, QMainWindow, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem
import pyqtgraph as pg
# from PyQt5 import QtGui
import inspect
# Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class InspectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.setWindowTitle('Light Work')

        ########################################################## experiment objects tab ################################################
        self.instruments_tab = QWidget()
        self.tabWidget.addTab(self.instruments_tab, "Experiment Objects")
        vertical_layout = QVBoxLayout()
        self.instruments = {}
        self.instruments_combobox = QComboBox()
        self.instruments_combobox.addItems(self.generate_all_possible_instruments(fullname=True))
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.instruments_combobox)
        add_object_button = QPushButton('Add Experiment Object')
        add_object_button.clicked.connect(self.add_instrument)
        horizontal_layout.addWidget(add_object_button)
        delete_object_button = QPushButton('Delete Experiment Object')
        delete_object_button.clicked.connect(self.delete_instrument)
        horizontal_layout.addWidget(delete_object_button)
        vertical_layout.addLayout(horizontal_layout)
        self.instruments_tree = QTreeWidget()
        vertical_layout.addWidget(self.instruments_tree)
        self.instruments_tab.setLayout(vertical_layout)
        
        ########################################################## RTC tab ################################################
        self.RTC_tab = QWidget()
        self.RTC_tab.layout = QGridLayout()
        self.tabWidget.addTab(self.RTC_tab, "RTC")
        ########################################################## scan tab ################################################
        self.scan_tab = QWidget()
        self.scan_tab.layout = QGridLayout()
        self.tabWidget.addTab(self.scan_tab, "Scan")
        

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
    
    def generate_all_possible_instruments(self, fullname=True):
        object_options = self.all_classes_in_dir(os.path.dirname(s.__file__))
        object_options.extend(self.all_classes_in_dir(os.path.dirname(m.__file__)))
        if fullname == False:
            object_options = [i.split('MeasurementObject')[0].split('ScanObject')[0]for i in object_options]
        return object_options

    def delete_instrument(self):
        pass

    def add_instrument(self):
        self.define_instrument_dialog = QDialog()
        object_to_add = self.instruments_combobox.currentText()
        if 'Measurement' in object_to_add:
            instrument_class = getattr(importlib.import_module('.{}'.format(object_to_add), 'LightWork.MeasurementObjects'), '{}'.format(object_to_add))
        else:
            instrument_class = getattr(importlib.import_module('.{}'.format(object_to_add), 'LightWork.ScanObjects'), '{}'.format(object_to_add))
        sig = inspect.signature(instrument_class)
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
            newitem = QTableWidgetItem(str(value))
            argument_table.setItem(0, count, newitem)
            argument_table.setHorizontalHeaderItem(count, QTableWidgetItem(key))
        argument_table.setVerticalHeaderItem(0, QTableWidgetItem(object_to_add))
        argument_table.resizeColumnsToContents()
        argument_table.resizeRowsToContents()
        
        verticalLayout = QVBoxLayout(self.define_instrument_dialog)
        verticalLayout.addWidget(argument_table)
        buttonBox = QDialogButtonBox(self.define_instrument_dialog)
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        verticalLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(lambda: self.save_instrument(instrument_class, argument_table))
        buttonBox.rejected.connect(self.define_instrument_dialog.close)
        self.define_instrument_dialog.setLayout(verticalLayout)
        self.define_instrument_dialog.setWindowTitle("Define parameters for {}".format(object_to_add))
        self.define_instrument_dialog.resize(200*len(arguments.keys()), 200)
        self.define_instrument_dialog.show()
    
    def save_instrument(self, instrument_class, argument_table):
        # Generate argument dictionary from argument table
        arguments = {}
        for column in range(argument_table.columnCount()):
            arguments[argument_table.horizontalHeaderItem(column).text()] = argument_table.item(0, column).text()
            
        # Because python doesn't allow us to enforce argument type, we need to map everything to the correct data type
        sig = inspect.signature(instrument_class)
        for key, value in arguments.items():
            # Need some sort of error handling when the user input does not evaluate. I am not a fan of how it is right now
            error = False
            if not value:
                self.define_instrument_dialog.close()
                error = True
                raise Exception("Invalid syntax in scan_values argument")
                
            if sig.parameters[key].default is not sig.parameters[key].empty:
                arguments[key] = type(sig.parameters[key].default)(value) # map the argument to the type of the default argument
            elif 'scan_values' in key:
                try:
                    val = eval(value)
                    arguments[key] = val
                except SyntaxError:
                    error = True
                    raise Exception("Invalid syntax in scan_values argument")
                    
        if not error:
            self.instruments[arguments['name']] = instrument_class(**arguments)
            self.update_instruments_tree_widget(arguments)
            self.define_instrument_dialog.close()
            

    def update_instruments_tree_widget(self, arguments):
        instrument_key = arguments['name']
        item_to_add = QTreeWidgetItem([instrument_key])
        print(arguments['scan_values'])
        for key, value in arguments.items():
            value_child = QTreeWidgetItem()
            value_child.setText(0, str(value))
            key_child = QTreeWidgetItem()
            key_child.setText(0, str(key))
            key_child.addChild(value_child)
            item_to_add.addChild(key_child)
        self.instruments_tree.addTopLevelItem(item_to_add)
        item_to_add.setExpanded(True)
    
        

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
    MainWindow.showMaximized()
    sys.exit(app.exec_())
# %%
