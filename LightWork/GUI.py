import glob
import numpy as np
import os
import importlib
import LightWork.MeasurementObjects.TestMeasurementObject as m
import LightWork.ScanObjects.TestScanObject as s
from PyQt5.QtCore import QTimer, Qt, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QPushButton, QDialog, QTabWidget, QGridLayout, QWidget, QComboBox, QTableWidget, 
                             QDoubleSpinBox, QCheckBox, QTableWidgetItem, QMainWindow, QDialogButtonBox, QVBoxLayout, QHBoxLayout, 
                             QTreeWidget, QTreeWidgetItem, QLineEdit, QLabel
                             )
from LightWork.ParentClasses.SpecPlotGUIElement import SpecPlotGUIElement
import pyqtgraph as pg
import inspect
import sip
import time
# Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

# Real-time-capture Worker thread class
class Worker(QObject):
    data = pyqtSignal(object)
    def __init__(self, exposure):
        super().__init__()
        self.exposure = exposure
        self.yaxis_key = None
        self.measurement_instrument = None
        self.poller = QTimer(self) # setting up a timer to substitute the need of a while loop for the RTC
        self.poller.timeout.connect(self._polling_routine) # this is the function the timer calls upon on every timeout
        
    # def _polling_routine(self):
    #     time.sleep(2)
    #     dat = np.random.randint(0,10)
    #     print(dat)
    #     self.data.emit(dat) # replace with camera acquisition
        
    def _polling_routine(self):
        dat = self.measurement_instrument.measure()[self.yaxis_key]
        self.data.emit(dat) 
    
    def polling_toggle(self):
        if self.poller.isActive():
            self.poller.stop()
        else:
            self.poller.start(self.exposure)
    

# Main window class
class InspectionWindow(QMainWindow):
    RTC_emit_start =  pyqtSignal(str)
    RTC_emit_stop = pyqtSignal()
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
        self.RTC_plot_domain = None # use none as sentinel value
        self.RTC_tab = QWidget()
        self.RTC_widgets = {}
        self.RTC_tab.layout = QHBoxLayout()
        self.RTC_tab.setLayout(self.RTC_tab.layout)
        self.tabWidget.addTab(self.RTC_tab, "RTC")
        ########################################################## scan tab ################################################
        self.scan_tab = QWidget()
        self.scan_tab.layout = QGridLayout()
        self.tabWidget.addTab(self.scan_tab, "Scan")
        
        self.timer = QTimer()
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.eventLoop)
        self.timer.start()
    
    def toggle_RTC(self):
        # need to clean this up and find a way to generalize to all instruments...
        if self.RTC_widgets['{}_RTC_checkbox'.format(self.measurement_instrument_name)].isChecked():
            self.worker.measurement_instrument = self.instruments[self.measurement_instrument_name]
            self.worker.measurement_instument.exposure_in_s = self.RTC_widgets['{}_exposure'.format(self.measurement_instrument_name)].value()
            self.worker.exposure = self.RTC_widgets['{}_exposure'.format(self.measurement_instrument_name)].value()
            self.worker.yaxis_key = self.RTC_widgets['{}_yaxis_combobox'.format(self.measurement_instrument_name)].text()
            self.RTC_emit_start.emit()
        else:
            self.RTC_emit_stop.emit()
    
    def update_RTC_plot(self, data):
        # Need to execute this correctly
        if self.RTC_plot_domain is not None:
            self.RTC_widgets['{}_SpecPlot'.format(self.measurement_instrument_name)].setData(self.RTC_plot_domain, data)
        else:
            print(data)
      
    def create_RTC_worker_thread(self, measurement_instrument, yaxis_key, exposure):    
        self.thread = QThread()
        self.worker = Worker(measurement_instrument, yaxis_key, exposure)
        self.worker.moveToThread(self.thread)
        self.worker.data.connect(self.update_RTC_plot) 
        self.RTC_emit_start.connect(self.worker.polling_toggle)
        self.RTC_emit_stop.connect(self.worker.polling_toggle)

        self.thread.start()

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
        current = self.instruments_tree.currentItem()
        while current.parent():
            current = current.parent()
        name = current.text(0)
        inst_class_name = type(current).__name__
        if 'Measurement' in inst_class_name:
            sip.delete(self.RTC_widgets['{}_SpecPlot'.format(name)])
            sip.delete(self.RTC_widgets['{}_exposure_label'.format(name)])
            sip.delete(self.RTC_widgets['{}_exposure'.format(name)])
            sip.delete(self.RTC_widgets['{}_yaxis_combobox'.format(name)])
            sip.delete(self.RTC_widgets['{}_RTC_checkbox'.format(name)])
            sip.delete(self.RTC_widgets['{}_layout'.format(name)])
            del self.RTC_plot_domain
        else:
            sip.delete(self.RTC_widgets['{}_label'.format(name)])
            sip.delete(self.RTC_widgets['{}_text_input'.format(name)] )
            sip.delete(self.RTC_widgets['{}_button'.format(name)])
            sip.delete(self.RTC_widgets['{}_layout'.format(name)])
        sip.delete(current)
        del self.instruments[name]

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
        # Create argument table
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
        self.define_instrument_dialog.resize(500*len(arguments.keys()), 200)
        self.define_instrument_dialog.show()
    
    def save_instrument(self, instrument_class, argument_table):
        # Generate argument dictionary from argument table
        arguments = {}
        for column in range(argument_table.columnCount()):
            arguments[argument_table.horizontalHeaderItem(column).text()] = argument_table.item(0, column).text()
        
        # map everything to the correct data type
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
        if arguments['name'] in self.instruments.keys():
            error = True
            raise Exception("Name is already assigned to an instrument")
            
        if not error:
            self.define_instrument_dialog.close()
            self.instruments[arguments['name']] = instrument_class(**arguments)
            self.update_instruments_tree_widget(arguments)
            self.generate_RTC_widget(arguments['name'])
            
    def update_instruments_tree_widget(self, arguments):
        instrument_key = arguments['name']
        item_to_add = QTreeWidgetItem([instrument_key])
        for key, value in arguments.items():
            value_child = QTreeWidgetItem()
            value_child.setText(0, str(value))
            key_child = QTreeWidgetItem()
            key_child.setText(0, str(key))
            key_child.addChild(value_child)
            item_to_add.addChild(key_child)
        self.instruments_tree.addTopLevelItem(item_to_add)
        item_to_add.setExpanded(True)
    
    def generate_RTC_widget(self, name):
        # get instance of instrument to generate
        inst = self.instruments[name]
        inst_class_name = type(inst).__name__
        if 'Measurement'in inst_class_name:
            # Generate x and y axis options by taking a sample measurement and using the return
            import pdb; pdb.set_trace()
            data = inst.measure()
            yaxis_combobox = QComboBox()
            for key, value in data.items():
                if 'wavelengths'in key or 'energies' in key:
                    self.RTC_plot_domain = np.array(value)
                else:
                    yaxis_combobox.addItems(key)
            
            self.measurement_instrument_name = name # it is useful to have this a attribute of the instance... not pretty though
            import pdb; pdb.set_trace()
            SpecPlot = SpecPlotGUIElement()
            SpecPlot.setData([650,750,850],[1,1,1])
            exposure = QDoubleSpinBox()
            exposure.setValue(1)
            RTC_checkbox = QCheckBox()
            RTC_checkbox.setText('Begin RTC')
            RTC_checkbox.stateChanged.connect(self.toggle_RTC)
            exposure_label = QLabel('Exposure [s]')
            layout = QVBoxLayout()
            layout.addWidget(SpecPlot)
            hlayout = QHBoxLayout()
            hlayout.addWidget(exposure_label)
            hlayout.addWidget(exposure)
            hlayout.addwidget(yaxis_combobox)
            hlayout.addWidget(RTC_checkbox)
            layout.addLayout(hlayout)
            self.RTC_widgets['{}_SpecPlot'.format(name)] = SpecPlot
            self.RTC_widgets['{}_exposure_label'.format(name)] = exposure_label
            self.RTC_widgets['{}_exposure'.format(name)] = exposure
            self.RTC_widgets['{}_yaxis_combobox'.format(name)] = yaxis_combobox
            self.RTC_widgets['{}_RTC_checkbox'.format(name)] = RTC_checkbox
            self.RTC_widgets['{}_layout'.format(name)] = layout
            self.RTC_tab.layout.addLayout(layout)
            self.create_RTC_worker_thread(inst, yaxis_combobox.text(), exposure.value())
        else:
            units, current_value = inst.get_scan_value()
            layout = QVBoxLayout()
            label = QLabel('{}'.format(name))
            layout.addWidget(label)
            text_input = QLineEdit()
            text_input.setText(str(current_value))
            layout.addWidget(text_input)
            button = QPushButton('Go to {}'.format(units))
            button.clicked.connect(lambda: inst.set_scan_value(float(text_input.text())))
            layout.addWidget(button)
            #Store widgets in dict so that they can be referenced later
            self.RTC_widgets['{}_label'.format(name)] = label
            self.RTC_widgets['{}_text_input'.format(name)] = text_input
            self.RTC_widgets['{}_button'.format(name)] = button
            self.RTC_widgets['{}_layout'.format(name)] = layout
            self.RTC_tab.layout.addLayout(layout)
            
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
