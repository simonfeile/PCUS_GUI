
import sys, os
# adds folder bellow
sys.path.append(os.path.join(os.path.dirname(sys.path[0])))


from PyQt5 import QtGui, QtWidgets, QtTest, uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from pathlib import Path
from PCUS_pro import *
from PCUS_dummy import *

import datetime
import numpy as np
import json

class Ui_MainWindow_functionality(QtWidgets.QMainWindow):

    def __init__(self):
        """ initialize the GUI_pcus and generate PCUS class"""
        super().__init__()
        #
        # uic.loadUi("test.ui",self)
        uic.loadUi("test.ui",self)
        self.PlotWidget.setLabel('bottom', "Time", units='µs')
        self.PlotWidget.setYRange(-1,1)


        sshFile = "Combinear.qss"       #import style
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())

        self.add_functionality()
        # self.applysetting()

        self.filepath = ""
        self.Start_Measurement_Series_Button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.Snapshot.setEnabled(False)
        self.DisconnectButton.setEnabled(False)

        GUI_json = Path('init_GUI_dict.json')
        if GUI_json.is_file():
            with open(GUI_json, 'r') as fp:
                init_GUI_settings_dict = json.load(fp)
                self.set_settings_from_dict(init_GUI_settings_dict)
                self.write_GUI_params()

    def add_functionality(self):
        """ add functionality to buttons """
        self.ConnectButton.clicked.connect(self.connect)
        self.DisconnectButton.clicked.connect(self.disconnect)
        # self.Snapshot.clicked.connect(self.snapshot(True,True,False))
        self.Snapshot.clicked.connect(lambda: self.snapshot(True,True,False))
        self.calibrate_button.clicked.connect(lambda: self.start_snapshot_series(True,True,False))
        self.stop_calibration.clicked.connect(self.stop_snapshot_series)
        self.Stop_Measurement_Series_Button.clicked.connect(self.stop_snapshot_series)
        self.Browse_button.clicked.connect(self.browse_select_folder)
        self.actionSaveAscan.triggered.connect(lambda: self.save_current_shot_as_ascan(True))
        self.Start_Measurement_Series_Button.clicked.connect(self.start_series)

    def connect(self):

        if bool(self.Device_Combo_Box.currentIndex()):
            self.pcus = PCUS_dummy()
            self.ImpulseDelaySpinBox.setEnabled(False)
            self.ImpulseLengthSpinBox.setEnabled(False)
            self.ImpulseVoltageSpinBox.setEnabled(False)
            self.PulseEchocomboBox.setEnabled(False)
        else:
            self.pcus = PCUS_pro()



        self.pcus.SearchAndOpenPCUSDevice()


        msg = QMessageBox()
        msg.setWindowTitle("")
        msg.setText("connected")
        x = msg.exec()
        self.ConnectButton.setEnabled(False)
        self.DisconnectButton.setEnabled(True)
        self.Start_Measurement_Series_Button.setEnabled(True)
        self.calibrate_button.setEnabled(True)
        self.Snapshot.setEnabled(True)

        # load the PCUS init json
        pcus_json = Path('../init_pcus_dict.json')
        if pcus_json.is_file():
            with open(pcus_json, 'r') as fp:
                init_settings_dict = json.load(fp)
                self.pcus.set_settings_from_dict(init_settings_dict)
                self.read_settings_from_pcus_to_GUI()

    def disconnect(self):
        self.series_bool = False
        current_settings_dict = self.pcus.get_current_settings_as_dict()
        with open('../init_pcus_dict.json', 'w') as fp:
            json.dump(current_settings_dict, fp, indent=4)

        current_GUI_settings_dict = self.get_current_settings_as_dict()
        with open('init_GUI_dict.json', 'w') as fp:
            json.dump(current_GUI_settings_dict, fp, indent=4)


        self.pcus.ClosePCUSDevice()
        msg = QMessageBox()
        msg.setWindowTitle("")
        msg.setText("disconnected and settings saved")
        x = msg.exec()
        self.ConnectButton.setEnabled(True)
        self.DisconnectButton.setEnabled(False)
        self.Start_Measurement_Series_Button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.Snapshot.setEnabled(False)

        self.ImpulseDelaySpinBox.setEnabled(True)
        self.ImpulseLengthSpinBox.setEnabled(True)
        self.ImpulseVoltageSpinBox.setEnabled(True)
        self.PulseEchocomboBox.setEnabled(True)


    def display_plot(self):
        self.PlotWidget.clear()

        # print(self.completedata[:20])
        # self.completedata= self.GainSpinBox.value() *np.linspace(0,100,100)
        delay_in_us = self.pcus.GetRecordingDelay()
        recordinglength_in_us = self.pcus.GetRecordingLength()

        # print(f"recordinglength_in_us {recordinglength_in_us}")

        #time in mikro seconds
        time = np.linspace(0+delay_in_us,delay_in_us+recordinglength_in_us,self.pcus.RecordingLength)
        self.PlotWidget.plot(time,self.completedata)


        # self.PlotWidget.setLabel('left', "Y Axis", units='A')
        self.PlotWidget.setLabel('bottom', "Time", units='µs')
        self.PlotWidget.setYRange(-1,1)



    def snapshot(self, apply_settings_flag = True, display_measurement_flag = True, save_measurement_flag = False):
        """takes a snapshot"""
        # print(apply_settings_flag)
        if apply_settings_flag:
            self.applysetting()
            # print("settings applied")
        self.completedata = self.pcus.Snapsshot()

        if display_measurement_flag:
            self.display_plot()

        if save_measurement_flag:
            # print("save function called")
            self.save_current_shot_as_ascan()

        QtTest.QTest.qWait(self.idle_time)

    def start_snapshot_series(self, apply_settings_flag = True, display_measurement_flag = True, save_measurement_flag = False):
        self.series_bool = True
        self.Snapshot.setEnabled(False)
        self.calibrate_button.setStyleSheet("background-color:#b78620")
        while self.series_bool:
            self.snapshot(apply_settings_flag, display_measurement_flag, save_measurement_flag)


    def stop_snapshot_series(self):
        self.series_bool = False
        self.calibrate_button.setEnabled(True)
        self.Snapshot.setEnabled(True)
        self.calibrate_button.setStyleSheet("background-color:qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(84, 84, 84, 255),stop:1 rgba(59, 59, 59, 255));")


    def browse_select_folder(self):
        self.filepath = str(QFileDialog.getExistingDirectory(self
                                                    , options=QFileDialog.DontUseNativeDialog)) # doesnt work for pyqt6
        self.PathDisplay.setPlainText(str(self.filepath))

    def browse_select_filename(self):
        select_file_name = QFileDialog.getSaveFileName(self,"select folder and type in filename",self.filepath
                                                    , options=QFileDialog.DontUseNativeDialog)
        return select_file_name[0]

    def apply_settings_from_GUI_to_PCUS(self):
        """
        reads out the GUI_pcus and applies it to PCUS
        :return: 
        """
        # PCUS settings ---------------------------------------
        self.pcus.SetImpulseLength(float(self.ImpulseLengthSpinBox.value()))
        self.pcus.SetImpulseVoltage(float(self.ImpulseVoltageSpinBox.value()))

        self.pcus.SetImpulseDelay(float(self.ImpulseDelaySpinBox.value()))
        self.pcus.SetRecordingDelay(float(self.RecordingDelaySpinBox.value()))
        self.pcus.SetRecordingLength(int(self.RecordingLengthSpinBox.value()))

        self.pcus.SetGain(float(self.GainSpinBox.value()))
        self.pcus.SetFilter(int(self.FiltercomboBox.currentIndex()))
        self.pcus.SetPreampEnabled(bool(self.PreAmpcomboBox.currentIndex()))
        self.pcus.SetDualInputMode(bool(self.PulseEchocomboBox.currentIndex()))

        self.pcus.SetShotsToAverage(self.RecordingAverageSpinBox.value())
        self.pcus.ApplyMeasurementSettings()  # transfers settings from pcus class to device

    def read_settings_from_pcus_to_GUI(self):
        """
        reads the settings from PCUS and applies to GUI_pcus
        :return: 
        """
        #Mode
        self.PulseEchocomboBox.setCurrentIndex(self.pcus.GetDualInputMode())
        # Sender
        self.ImpulseDelaySpinBox.setValue(self.pcus.GetImpulseDelay())
        self.ImpulseLengthSpinBox.setValue(int(self.pcus.GetImpulseLength()))
        self.ImpulseVoltageSpinBox.setValue(int(self.pcus.GetImpulseVoltage()))
        # Receiver
        self.RecordingDelaySpinBox.setValue(float(self.pcus.GetRecordingDelay()))
        self.RecordingLengthSpinBox.setValue(int(self.pcus.GetRecordingLength()))
        self.RecordingAverageSpinBox.setValue(int(self.pcus.GetShotsToAverage()))
        # Amplifier & filter
        self.GainSpinBox.setValue(int(self.pcus.GetGain()))
        self.PreAmpcomboBox.setCurrentIndex(self.pcus.GetPreampEnabled())
        self.FiltercomboBox.setCurrentIndex(int(self.pcus.GetFilter()))

    def read_GUI_params(self):
        """read out GUI_pcus to internat parameters"""
        self.sample_name = str(self.samplenameLabel.text())
        self.wait_time = int(self.Wait_Time_SpinBox.value())
        self.NumberOfMeasurement = int(self.NumberOfMeasurementSpinBox.value())
        self.EndlessMode = bool(self.EndlessModeCheckBox.isChecked())
        self.LiveView = bool(self.LiveViewCheckbox.isChecked())
        self.filepath = str(self.PathDisplay.toPlainText())

    def write_GUI_params(self):
        """write internal parameters to GUI_pcus"""
        self.samplenameLabel.setText(self.sample_name)
        self.Wait_Time_SpinBox.setValue(self.wait_time)
        self.NumberOfMeasurementSpinBox.setValue(self.NumberOfMeasurement)
        self.EndlessModeCheckBox.setChecked(self.EndlessMode)
        self.LiveViewCheckbox.setChecked(self.LiveView)
        self.PathDisplay.setPlainText(str(self.filepath))

    def get_current_settings_as_dict(self):
        """ get current internal settings as dict"""
        settings_dict = \
            {
                "Sample Name: ": self.sample_name,
                "Time between measurements [s]: ": self.wait_time,
                "Total number of measurements: ": self.NumberOfMeasurement,
                "Endless mode: ": self.EndlessMode,
                "LiveViewCheckbox: ": self.LiveView,
                "LastSavePath: ": self.filepath
            }
        # print(json.dumps(self.settings_dict, indent=4))
        return settings_dict

    def set_settings_from_dict(self,settings_dict):
        """ set current internal settings from dict"""
        self.sample_name = settings_dict["Sample Name: "]
        self.wait_time = settings_dict["Time between measurements [s]: "]
        self.NumberOfMeasurement = settings_dict["Total number of measurements: "]
        self.EndlessMode = settings_dict["Endless mode: "]
        self.LiveView = settings_dict["LiveViewCheckbox: "]
        self.filepath = settings_dict["LastSavePath: "]

    def applysetting(self):
        """
        Applies the settings from the GUI_pcus
        will be called after connecting and before every snapshot or measurement in calibrate
        :return:
        """
        self.apply_settings_from_GUI_to_PCUS()
        self.idle_time = int(600 + self.pcus.GetShotsToAverage() * 10)  # defines idletime in ms after shot
        self.read_GUI_params()




        #------------------------------GUI_pcus settings-------------

        #
        # print("settings Applied")
        # print(f'gain: {self.GainSpinBox.value()}')
        # print(f'gain in PCus: {self.pcus.Gain}')
        #

    def save_current_shot_as_ascan(self,chose_path_and_name_flag = False):
        """ saves current shot as ascan"""
        settings_dict_pcus = self.pcus.get_current_settings_as_dict() # these are the Measurement parameters set in PCUS

        now = datetime.datetime.now()
        date = str(now.strftime("%Y_%m_%d_%H_%M_%S"))
        filename = self.sample_name + '_' + date + '.ascan'

        if chose_path_and_name_flag:   # define fielpath of not defined
            savename = self.browse_select_filename() +date+ '.ascan'
        else:
            savename = self.filepath  + '/' + filename

        with open(savename, 'w') as filehandle:
            for (key, value) in settings_dict_pcus.items():
                filehandle.write(str(key) + ': ' + str(value) + '\n')
            filehandle.write('\n')
            filehandle.write('ShotIndex;Amplitudes\n')
            for line in self.completedata:
                filehandle.write('%f;' % line)
        filehandle.close()
        # print('Measurement with index ' + str(x) + ' finished. Waiting for next repetition.')

    def start_series(self):
        """ starts a measurement series with current settings"""
        self.applysetting()
        self.calibrate_button.setEnabled(False)
        self.Snapshot.setEnabled(False)
        self.series_bool = True
        wait_time = self.wait_time*1000 - self.idle_time # in ms
        # print(f'faittime { wait_time}')
        self.change_progress_bar(0)
        if self.EndlessMode:
            index = 0
            while self.series_bool:
                self.snapshot(apply_settings_flag = False, display_measurement_flag = bool(self.LiveViewCheckbox.isChecked())
                              , save_measurement_flag= True)
                index += 1
                self.change_progress_bar(index)
                QtTest.QTest.qWait(wait_time)
        else:
            for i in range(self.NumberOfMeasurement):
                # print(i)
                if not self.series_bool:
                    # print("broke")
                    break
                self.snapshot(apply_settings_flag = False, display_measurement_flag = bool(self.LiveViewCheckbox.isChecked())
                              , save_measurement_flag= True)
                self.change_progress_bar(i + 1)
                QtTest.QTest.qWait(wait_time)

        self.progressLineEdit.setText("complete")
        self.calibrate_button.setEnabled(True)
        self.Snapshot.setEnabled(True)

    def change_progress_bar(self,index):
        if self.EndlessMode:
            self.progressLineEdit.setText(str(int(index)))
            self.progressBar.setValue(int(100))
        else:
            self.progressLineEdit.setText(str(int(index)) + "/" + str(int(self.NumberOfMeasurement)))
            self.progressBar.setValue(int(index/int(self.NumberOfMeasurement)*100))

if __name__ == "__main__":
    def main():
        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon('iconPCUS-Interface.ico'))


        # MainWindow = QtWidgets.QMainWindow()
        # ui = Ui_MainWindow_functionality()
        w = Ui_MainWindow_functionality()
        # ui.setupUi(MainWindow)
        w.show()
        sys.exit(app.exec())


    main()