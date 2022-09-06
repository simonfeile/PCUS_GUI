import sys
from scipy.interpolate import interp1d
import numpy as np
import scipy.signal as sg
import matplotlib.pyplot as plt
import datetime
import os



def read_pcus_ascan(file):
    """
    reads pcus ascan as defined in the pcus class
    Parameters
    ----------
    file : filename or buffer
        Describes location of the to read .ascan file
    Returns
    -------
    ascan_dict : dict
        Contains the lines of the .ascan file as key-value pairs. One of them are the amplitude values
    """
    ascan_file = open(file, encoding='utf-8')
    # dictionary to hold the lines:
    ascan_dict = dict()
    # loop through the file's lines
    for line in ascan_file:
        if ':' in line:
            split_line = line.split(':')
            key = split_line[0]
            split_1 = split_line[1].split('\n')[0]
            try:
                value = float(split_1)  # its a float or int
            except ValueError:  # its not a float or int
                if 'None' in split_1:
                    value = None
                elif 'False' in split_1:
                    value = False
                elif 'True' in split_1:
                    value = True
                else:
                    value = split_1  # its a string
            ascan_dict[key] = value
        elif ';' in line:  # should be True for the last two lines
            split_line = line.split(';')
            try:
                split_0 = float(split_line[0])
            except ValueError:
                split_0 = split_line[0]
            if type(split_0) == float:
                value_0 = split_0
                values_array = np.array(split_line[1:-2])  # first value = index, last value is \n
            else:
                key_0 = split_0.split('\n')[0]
                key_1 = split_line[1].split('\n')[0]
        else:  # empty lines
            pass
    try:
        type(key_0)
        ascan_dict[key_0] = value_0  # key should be ShotIndex
        ascan_dict[key_1] = values_array  # key should be Amplitudes
    except NameError:
        print('The passed file does not contain amplitude values!')
    ascan_file.close()
    return ascan_dict


class US_data_single_file_class():
    """
    container for single US_data file
    and analysis
    """
    def __init__(self,filename, amp_treshhold):
        """
        :param filename: full path of US file to be analysed
        :param amp_treshhold: threshhold of amplitude
        """
        # define variables
        self.filename = filename
        self.amp_treshhold = amp_treshhold
        # call functions
        self.read_ascan(self.filename)
        self.envelope_and_indices()
        self.max_amp()
        self.ToF_threshold_of_amp()


    def read_ascan(self,filename):
        """
        reads in PCUS ascan file
        :param filename:
        :return:
        """
        datetime_string = filename[-25:-6]
        self.time_of_recording = datetime.datetime.strptime(datetime_string, "%Y_%m_%d_%H_%M_%S")
        pcus_dict = read_pcus_ascan(filename)
        Amplitudes = pcus_dict['Amplitudes']
        Amplitude_float = []

        for amp in Amplitudes:
            try:
                amp_float = float(amp)
            except ValueError:
                if "--" in amp:
                    amp_float = float(amp[1:])

            Amplitude_float.append(amp_float)

        self.amplitude = np.array(Amplitude_float)

        # delete the Amplitudes to pass rest to logging
        del pcus_dict['Amplitudes']
        print(f"filename {filename}")
        if 'Sampling rate' in pcus_dict:
            self.sr = float(pcus_dict['Sampling rate'])
        else:
            self.sr = 100 * 1e6 # for pcus measurements


        print(f'Smapling rate of file {self.sr/1e6} MHz')
        si = 1 / self.sr
        n_sa = len(Amplitude_float)
        if 'RecordingDelay [us]' in set(pcus_dict.keys()):
            delay = pcus_dict['RecordingDelay [us]'] * 1e-6
        elif 'Recording delay [ns]' in set(pcus_dict.keys()):
            delay = pcus_dict['Recording delay [ns]'] * 1e-9
        # print(f'delay {delay}')
        self.time = np.linspace(delay, delay + si * (n_sa - 1), num=n_sa)




    def envelope_and_indices(self):
        """
        calculates the envelope of the signal and the indices of search windows
        :return:
        """
        self.abs_amp = np.abs(self.amplitude)
        self.analytical_signal = sg.hilbert(self.amplitude)
        self.envelope = np.abs(self.analytical_signal)

        self.max_amp()


    def max_amp(self):
        """
        find maximum of envelope in time and value
        :return:
        """
        self.max_envelope = np.max(self.envelope)
        self.time_max_amp =  self.time[np.argwhere(self.envelope == self.max_envelope)[0][0]]


    def ToF_threshold_of_amp(self):
        """
        takes filename returns interpolated self.threshold__of_amp ToF
        :param filename:
        :return:
        """
        threshold = self.max_envelope * self.amp_treshhold

        # find the index of first value over threshhold
        envth_arg = np.argmax(self.abs_amp > threshold)

        # this is to prevent errors in next step
        if envth_arg < 3:
            envth_arg = 3


        sign = np.sign(self.amplitude[envth_arg])

        # amp and time values around envth_arg
        amplitude_interp = self.abs_amp[envth_arg - 1: envth_arg + 1]
        time_interp = self.time[envth_arg - 1: envth_arg + 1]

        #interpolation
        interpolation = interp1d(time_interp, amplitude_interp)
        time_fluent = np.linspace(self.time[envth_arg - 1], self.time[envth_arg], 200, True) # maybe 100 will suffice

        #find the index of first value over threshhold for interpolated signal
        envth_arg_interp = np.argmax(interpolation(time_fluent) > threshold)
        self.tof_threshold_of_amp = time_fluent[envth_arg_interp]

        self.threshold = interpolation(self.tof_threshold_of_amp)

        return self.tof_threshold_of_amp


    def simple_plot(self):
        plt.figure("simple_plot")
        plt.plot(self.time,self.amplitude, label = "amplitude")
        plt.plot(self.time,self.envelope, label = "envelope")
        plt.xlabel("time[s]")
        plt.ylabel("Amplitude")
        plt.scatter(self.time_max_amp, self.max_envelope, label="max_envelope")
        plt.scatter(self.tof_threshold_of_amp, self.threshold, label="thrshold of Amplitude")
        plt.legend()


if __name__ == "__main__":

    # get complete file path
    file_path = os.getcwd() + "/US_example_data/SP_021_RPT_400Cycles_2022_01_17_18_30_40.ascan"

    # chose amp threshhold
    amp_threshhold = 0.1

    # create instance
    US_measurement = US_data_single_file_class(file_path,amp_threshhold)
    # plot
    US_measurement.simple_plot()
    plt.show()