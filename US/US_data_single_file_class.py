import sys
from scipy.interpolate import interp1d
import numpy as np
import scipy.signal as sg
import scipy.interpolate as sinter
import matplotlib.pyplot as plt
import datetime
import os
import sys
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-simon-feiler/Math')
sys.path.append('C:/Users/biologic/gitlab/phd-thesis-simon-feiler/Math')
from CrossCorr import cross_correlation_using_fft,compute_shift
from FourierTrafo import FourierTransform,Hamming_percentage,bandwidth

from FourierTrafo import bandwidth
from collections import OrderedDict
import pywt
from matplotlib import ticker, cm
import json
import pytz

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
    # try:
    #     if ascan_dict['Version'] != 3:
    #         print('The read_pcus_ascan function was adapted for "Version: 3" of the .ascan files. Deviation detected!')
    # except KeyError:
    #     print('There is no "Version" stated in the .ascan file!')
    # Don't forget to close the file at the end
    ascan_file.close()

    return ascan_dict

def argsstring(dict):
    args = ""

    for key in dict:
        if str(type(dict[key])) == "<class 'str'>" :
            args += f"""{key} = "{str(dict[key])}","""
        else:
            args += f"""{key} = {str(dict[key])},"""
    args = args[:-1]#remove last comma
    return args


class US_data_single_file_class():
    """
    container for single US_data file
    and analysis
    """
    def __init__(self,directory,filename,livedata,begin_noise, end_noise,
                 end_search_window, time = [0,0],amp = [0,0]):
        """
        :param filename: filename US file
        :param plot: bool : plotten
        :param livedata: : bool, if true directly supplied time and amp will be used
        :param time: directly supplied time
        :param amp: directly supplied amp
        """
        print(f"init directory {directory}")
        print(f"init filename {filename}")

        self.directory = directory
        self.filename = filename
        self.begin_noise = begin_noise
        self.end_noise = end_noise
        self.end_search_window = end_search_window
        self.anawindow_left_time = 0


        self.toF_threshold_of_noises = {}
        self.tof_threshold_of_amps = {}

        self.log = {}
        self.log["function_calls"] = OrderedDict()
        self.log["params"] = {}

        params = OrderedDict()
        params["directory"] = directory
        params["filename"] = filename
        params["livedata"] = livedata
        params["begin_noise"] = begin_noise
        params["end_noise"] = end_noise
        params["end_search_window"] = end_search_window
        params["time"] = time
        params["amp"] = amp

        self.log["__init__"] = {}
        self.log["__init__"][f"({argsstring(params)})"] = params


        self.figures = {}
        self.axis = {}
        self.filename = str(directory) +"/"+ filename

        if livedata:
            self.live_data(time,amp)

        else:
            self.read_ascan(self.filename)


        #
        self.cut_signal()
        self.envelope_and_indices()
    def live_data(self,time,amp):
        """
        should livedata be provided
        :param time:
        :param amp:
        :return:
        """
        self.time_of_recording = datetime.datetime.now()
        self.amplitude = np.array(amp)
        self.time = np.array(time)

        self.sr = 1/(time[100]-time[0])*100
        self.log["params"]["original_sampling_rate"] = self.sr
    def read_ascan(self,filename):
        """
        reads in PCUS ascan file
        :param filename:
        :return:
        """
        datetime_string = filename[-25:-6]
        self.time_of_recording = datetime.datetime.strptime(datetime_string, "%Y_%m_%d_%H_%M_%S")
        berlin = pytz.timezone('Europe/Berlin')
        # define as german tz
        self.time_of_recording = berlin.localize(self.time_of_recording)
        #convert to UTC
        self.time_of_recording  = self.time_of_recording.astimezone(pytz.utc)

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


        self.log["params"] ["original_sampling_rate"] = self.sr
        for key in pcus_dict:
            self.log["params"] [key] = pcus_dict[key]


        print(f'Smapling rate of file {self.sr/1e6} MHz')
        si = 1 / self.sr
        n_sa = len(Amplitude_float)
        if 'RecordingDelay [us]' in set(pcus_dict.keys()):
            delay = pcus_dict['RecordingDelay [us]'] * 1e-6
        elif 'Recording delay [ns]' in set(pcus_dict.keys()):
            delay = pcus_dict['Recording delay [ns]'] * 1e-9
        # print(f'delay {delay}')

        self.time = np.linspace(delay, delay + si * (n_sa - 1), num=n_sa)
    def downsample(self,factor):

        self.sr /= factor
        self.time = self.time [::factor]
        # self.amplitude = self.amplitude [::factor]
        self.amplitude = np.convolve(self.amplitude, np.ones(factor) / factor,mode='same')  # average M values
        self.amplitude = self.amplitude[::factor]

        self.log["function_calls"][f"downsample(factor = {factor})"] = {"factor":factor}

        print(f'Smapling rate after downlampling {self.sr / 1e6} MHz')
        # call envelope and indices to correct for new sampling rate
        self.envelope_and_indices()
    def cut_signal(self):
        """
        cuts signal to desired lenght = self.end_search_window
        :return:
        """

        if self.end_search_window > np.max(self.time):
            self.end_search_window = np.max(self.time)
        self.time_greater_max = np.argmax(self.time >= self.end_search_window)  # end of search window for tof

        self.amplitude = self.amplitude[:self.time_greater_max]
        self.time = self.time[:self.time_greater_max]
    def detrend_amplitude(self,type = 'linear'):
        self.amplitude = sg.detrend(self.amplitude, type=type)
        self.log["function_calls"][f"""detrend_amplitude(type = "{type}")"""] = {"type" : type}

        self.envelope_and_indices()
    def apply_Hamming_Window(self,percentage = 0.95):
        self.amplitude = Hamming_percentage(len(self.amplitude), percentage) * self.amplitude
        self.log["function_calls"][f"apply_Hamming_Window(percentage = {percentage})"] = {"percentage" : percentage}


        self.envelope_and_indices()
    def envelope_and_indices(self):
        """
        calculates the envelope of the signal and the indices of search windows
        :return:
        """
        self.abs_amp = np.abs(self.amplitude)
        
        if self.end_search_window > np.max(self.time):
            self.end_search_window = np.max(self.time)

        self.time_greater_min = np.argmax(self.time >= self.end_noise)    # beginning of search window for tof
        self.time_greater_max = np.argmax(self.time >= self.end_search_window) # end of search window for tof


        self.analytical_signal = sg.hilbert(self.amplitude)
        self.envelope = np.abs(self.analytical_signal)

        self.max_amp()
    def max_amp(self):
        """
        find maximum of envelope in time and value
        :return:
        """
        self.max_envelope = np.max(self.envelope[self.time_greater_min:self.time_greater_max])
        self.time_max_amp =  self.time[np.argwhere(self.envelope == self.max_envelope)[0][0]]
    def ToF_threshold_of_noise(self,multiplicator = 10):
        """
        takes filename returns interpolated self.threshold_of_noise_of_amp ToF
        :param filename:
        :return:
        """
        self.log["function_calls"][f"ToF_threshold_of_noise(multiplicator = {multiplicator})"] = {"multiplicator" : multiplicator}

        # amplitude that will be used for threshhold estimation
        noise_amp = self.amplitude[(self.time > self.begin_noise) & (self.time < self.end_noise)]
        # noise_amp = self.amplitude[50:250]
        # print(f'self.begin_noise {self.begin_noise}')
        # print(f'self.end_noise {self.end_noise}')
        # testing chosen amp
        # noise_time = self.time[(self.time > self.begin_noise) & (self.time < self.end_noise)]


        threshold = np.std(noise_amp) * multiplicator

        # find the index of first value over threshhold
        envth_arg = np.argmax(self.abs_amp[self.time_greater_min:self.time_greater_max] > threshold) + self.time_greater_min
        # this is to prevent errors in next step
        if envth_arg < 3:
            envth_arg = 3

        sign = np.sign(self.amplitude[envth_arg])

        # envelope and time values around envth_arg
        amplitude_interp = self.abs_amp[envth_arg - 1: envth_arg + 1]
        time_interp = self.time[envth_arg - 1: envth_arg + 1]

        #interpolation
        interpolation = interp1d(time_interp, amplitude_interp)
        time_fluent = np.linspace(self.time[envth_arg - 1], self.time[envth_arg], 200, True) # maybe 100 will suffice

        #find the index of first value over threshhold for interpolated signal
        envth_arg_interp = np.argmax(interpolation(time_fluent) > threshold)
        self.tof_threshold_of_noise = time_fluent[envth_arg_interp]

        threshold = interpolation(self.tof_threshold_of_noise)

        self.toF_threshold_of_noises[str(int(multiplicator))] = [self.tof_threshold_of_noise,sign*threshold]

        return self.tof_threshold_of_noise

    def ToF_threshold_of_amp(self,amp_frac = 0.1):
        """
        takes filename returns interpolated self.threshold__of_amp ToF
        :param filename:
        :return:
        """
        self.log["function_calls"][f"ToF_threshold_of_amp(amp_frac = {amp_frac})"] = {"amp_frac": amp_frac}


        threshold = self.max_envelope * amp_frac

        # find the index of first value over threshhold
        envth_arg = np.argmax(self.abs_amp[self.time_greater_min:self.time_greater_max] > threshold) + self.time_greater_min
        # this is to prevent errors in next step

        if envth_arg < 3:
            envth_arg = 3

        # envelope and time values around envth_arg
        sign = np.sign(self.amplitude[envth_arg])

        amplitude_interp = self.abs_amp[envth_arg - 1: envth_arg + 1]
        time_interp = self.time[envth_arg - 1: envth_arg + 1]

        #interpolation
        interpolation = interp1d(time_interp, amplitude_interp)
        time_fluent = np.linspace(self.time[envth_arg - 1], self.time[envth_arg], 200, True) # maybe 100 will suffice

        #find the index of first value over threshhold for interpolated signal
        envth_arg_interp = np.argmax(interpolation(time_fluent) > threshold)
        self.tof_threshold_of_amp = time_fluent[envth_arg_interp]

        threshold = interpolation(self.tof_threshold_of_amp)


        self.tof_threshold_of_amps[str(round(amp_frac,2))] = [self.tof_threshold_of_amp,sign*threshold]
        return self.tof_threshold_of_amp
    def estimate_spectral_analysis_window(self, th= 0.1, quick = False):
        """Estimates the boundaries of a window for a signal to be fed to spectral
        analysis based finding crossing points of a time series envelope with a
        horizontal line at a threshold th.

        Parameters
        ----------
        th : float
            Fraction of the maximum of the envelope. Values should lie between 0
            and 1.
        """



        # test if input values can be processed
        if th >= 1 or th <= 0:
            raise ValueError('Threshold th must lie in ]0, 1[!')
        norm = self.envelope / max(abs(self.envelope))
        # shifting the envelope on the y-axis, in way that the x-axis will cut it
        # at th
        y_reduced = np.array(norm) - th
        env_inter = sinter.UnivariateSpline(self.time, y_reduced, s=0, k=3)
        # finding crossing points of envelope and x-axis / horizontal line at th
        roots = env_inter.roots()
        roots_derivative = sinter.UnivariateSpline(self.time, y_reduced, s=0, k=4).derivative().roots()

        right_root = roots[np.argwhere(np.array(roots)>self.time_max_amp)[0][0]]
        left_root = roots[np.argwhere(np.array(roots)<self.time_max_amp)[-1][0]]

        try:
            anawindow_right_time = roots_derivative[np.argwhere(np.array(roots_derivative) > right_root)[0][0]]
        except IndexError:
            anawindow_right_time = self.time[len(self.time)-2]

        try:
            anawindow_left_time = roots_derivative[np.argwhere(np.array(roots_derivative) < left_root)[-1][0]]
        except IndexError:
            anawindow_left_time = self.time[1]

        anawindow_right_ind = np.argwhere(np.array(self.time) > anawindow_right_time)[0][0]
        anawindow_left_ind = np.argwhere(np.array(self.time) < anawindow_left_time)[-1][0]



        freq, X = self.fourier_trafo(plot=False, low=anawindow_left_ind, high=anawindow_right_ind)


        freq_max,freq_left,freq_right,bandwidth_percent = bandwidth(freq, X, db=6, type="amplitude")

        if quick:
            return anawindow_left_ind, anawindow_right_ind,freq, X,freq_max,freq_left,freq_right,bandwidth_percent


        self.log["function_calls"][f"estimate_spectral_analysis_window(th = {th})"] = {"th": th}

        self.anawindow_right_time = anawindow_right_time
        self.anawindow_left_time = anawindow_left_time

        self.anawindow_right_ind = anawindow_right_ind
        self.anawindow_left_ind = anawindow_left_ind
        self.freq = freq
        self.X = X

        self.freq_max = freq_max
        self.freq_left = freq_left
        self.freq_right = freq_right
        self.bandwidth_percent = bandwidth_percent
    def filter_amplitude(self,cut_off_freq0, cut_off_freq1, stop_band_attenuation, roll_off_width, plot = False,save = False):


        filter_dict = {}
        filter_dict["cut_off_freq0"] = cut_off_freq0
        filter_dict["cut_off_freq1"] = cut_off_freq1
        filter_dict["stop_band_attenuation"] = stop_band_attenuation
        filter_dict["roll_off_width"] = roll_off_width
        filter_dict["plot"] = plot



        self.log["function_calls"][f"filter_amplitude({argsstring(filter_dict)})"] = filter_dict

        if plot:
            self.plot_pre_filter("filter_amplitude")

        # Check input parameters
        if ((cut_off_freq0 or cut_off_freq1) <= 0) or ((cut_off_freq0 or cut_off_freq1) >= self.sr / 2):
            raise ValueError("The cut-off frequencies can not take values outside of 0 and fs/2 (exclusive)!")
        # Filter parameter
        rel_width = roll_off_width / self.sr
        num_of_taps, beta = sg.kaiserord(stop_band_attenuation, rel_width) # ref https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.kaiserord.html
        print(f'num_of_taps {num_of_taps}')
        print(f'beta {beta}')
        if num_of_taps % 2 == 0:  # has to be odd!
            num_of_taps += 1
        cut_off_freq = np.array([cut_off_freq0, cut_off_freq1])
        # Filter taps that will be applied to the signal. This is a bandpass, so pass_zero=False
        taps = sg.firwin(num_of_taps, cut_off_freq / self.sr*2, window=('kaiser', beta), pass_zero=False, scale=True)
        # print(f'taps {taps}')

        # taps, a = sg.butter(4, 3e6/self.sr)

        w, h = sg.freqz(taps,a=1, worN=80000)
        w *= 0.5 * self.sr / np.pi  # Convert w to Hz.

        self.amplitude = sg.filtfilt(b=taps, a=1, x=self.amplitude, padlen=len(self.amplitude) // 2 * 2 - 1)
        # output_signal = sg.filtfilt(b=b, a=1, x=self.amplitude, padlen=len(self.amplitude) // 2 * 2 - 1)
        self.envelope_and_indices()

        if plot:
            self.plot_post_filter("filter_amplitude",save)
            self.plot_filter_effects(w,h,save = False)
    def plot_pre_filter(self,name, labelprefix = ""):
        """
        plots the amplitude before aplying filters
        :param name:
        :param labelprefix:
        :return:
        """
        if labelprefix == "":
            self.figures[name],self.axis[name] = plt.subplots(1,2, gridspec_kw={'width_ratios': [2, 1]}, figsize = (16,9))
        self.axis[name][0].plot(self.time, self.amplitude, label=labelprefix+"amplitude")
        self.axis[name][0].plot(self.time, self.envelope, label=labelprefix+"envelope")

        anawindow_left_ind, anawindow_right_ind, freq, X, freq_max, freq_left, freq_right, bandwidth_percent = self.estimate_spectral_analysis_window(quick = True)
        if self.anawindow_left_time:
            anawindow_left_ind = self.anawindow_left_ind
            anawindow_right_ind = self.anawindow_right_ind
            freq, X = self.fourier_trafo(plot=False, low=anawindow_left_ind, high=anawindow_right_ind)
            freq_max, freq_left, freq_right, bandwidth_percent = bandwidth(freq, X, db=6, type="amplitude")



        self.axis[name][0].axvline(self.time[anawindow_left_ind], alpha=0.5, color="green",linestyle ="--")
        self.axis[name][0].axvline(self.time[anawindow_right_ind], label=labelprefix + "window", alpha=0.5, color="green",linestyle ="--")

        self.axis[name][1].plot(freq, X, label = labelprefix + "Fourier")
        self.axis[name][1].axvline(freq_max, label = labelprefix + str(round(freq_max / 1e6, 3)) + " MHz ("+ str(bandwidth_percent) + ")bw", alpha = 0.5, color = "black")

        self.axis[name][1].set_xlim(0, 0.4e7)
    def plot_post_filter(self, name, save = False):
        """
        plots the amplitude after aplying filters
        :param name:
        :return:
        """
        self.plot_pre_filter(name, labelprefix = "filtered ")
        self.axis[name][0].legend()
        self.axis[name][1].legend()
        if save:
            self.savefig(name)
    def plot_filter_effects(self,w,h,save = False):
        name = "plot_filter_effects"
        self.figures[name], self.axis[name] = plt.subplots(2, sharex=True)
        self.axis[name][0].plot(w, 20 * np.log10(abs(h))) # amplitude damping
        self.axis[name][0].set_ylabel("Magnitude[db]")
        self.axis[name][0].set_ylim(-40, 4)
        self.axis[name][1].plot(w, np.angle(h))
        self.axis[name][1].set_xlim(0, 1e7)
        self.axis[name][1].set_ylabel("Phase[radians]")
        self.axis[name][1].set_xlabel("frequency")
        if save:
            self.savefig(name)
    def sos_filter_amplitude(self,type,cut_off_freq0, cut_off_freq1, stop_band_attenuation,order,plot = False,save = False):
        """

        Parameters
        ----------
        cut_off_freq0 : float
            Lower cut-off frequency in Hz. Must be larger than 0.
        cut_off_freq1 : float or None
            Upper cut-off frequency in Hz. Must be smaller than fs/2

        stop_band_attenuation : float
            Stop band attenuation in dB
        roll_off_width : float
            Roll-off width in Hz
        Returns
        filtered data
        """

        filter_dict = OrderedDict()
        filter_dict["type"] = type
        filter_dict["cut_off_freq0"] = cut_off_freq0
        filter_dict["cut_off_freq1"] = cut_off_freq1
        filter_dict["stop_band_attenuation"] = stop_band_attenuation
        filter_dict["order"] = order
        filter_dict["plot"] = plot
        filter_dict["plot"] = save

        self.log["function_calls"][f"sos_filter_amplitude({argsstring(filter_dict)})"] = filter_dict

        if plot:
            self.plot_pre_filter("sos_filter_amplitude")

        # Check input parameters
        if ((cut_off_freq0 or cut_off_freq1) <= 0) or ((cut_off_freq0 or cut_off_freq1) >= self.sr / 2):
            raise ValueError("The cut-off frequencies can not take values outside of 0 and fs/2 (exclusive)!")
        # Filter parameter
        if type == "butter":
            sos = sg.butter(order,(cut_off_freq0, cut_off_freq1),btype='bandpass', output='sos',fs =self.sr)
        #
        elif type == "ellip":
            sos = sg.ellip(order, 0.001, stop_band_attenuation, (cut_off_freq0, cut_off_freq1), btype='bandpass'
                           ,output='sos',fs =self.sr)
        elif type == "bessel":
            sos = sg.bessel(order, (cut_off_freq0, cut_off_freq1), btype='bandpass'
                           ,output='sos',fs =self.sr, norm='phase')


        w, h = sg.sosfreqz(sos, worN=80000)
        w *= 0.5 * self.sr / np.pi  # Convert w to Hz.

        # pad = 10000
        # self.amplitude = np.concatenate((np.zeros(pad), self.amplitude,np.zeros(pad)))
        self.amplitude = sg.sosfiltfilt(sos, x=self.amplitude, padlen=len(self.amplitude) // 2 * 2 - 1)
        # self.amplitude = self.amplitude[pad:-pad]

        self.envelope_and_indices()

        # output_signal
        if plot:
            self.plot_post_filter("sos_filter_amplitude",save)
            self.plot_filter_effects(w, h,save = False)
        return
    def fourier_trafo(self , plot = False , low = 0, high =0):
        if low == 0:
            low = self.time_greater_min
        if high == 0:
            high = self.time_greater_max
        freq, X = FourierTransform(self.amplitude[low:high], self.sr, plot)

        return freq, X
    def short_time_fourier(self,time_intervall = 8e-6,zeropadding = 2**4,overlap = 5/6, plot = False, save = False):

        paramdict = OrderedDict()
        paramdict["time_intervall"] = time_intervall
        paramdict["zeropadding"] = zeropadding
        paramdict["overlap"] = overlap
        paramdict["plot"] = plot
        paramdict["save"] = save

        self.log["function_calls"][f"short_time_fourier({argsstring(paramdict)})"] = paramdict


        time_diff_ind  = time_intervall * self.sr
        potenz = int(np.log2(time_diff_ind))

        # print(f"potenz {potenz}")
        nperseg = 2**potenz
        nfft_factor = zeropadding * nperseg
        f, t, Zxx = sg.stft(self.amplitude, self.sr, window='hann',  nfft = nfft_factor, nperseg=nperseg
                                , noverlap=nperseg *overlap)
        t = np.array(t)+self.time[0]

        maximum = np.max(np.abs(Zxx))
        # plt.close("all")
        
        if plot:
            name = "stft"
            self.figures[name], self.axis[name] = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            self.axis[name][1].plot(self.time, self.amplitude)
    
            self.axis[name][1].axvline(self.time[0+20],alpha = 0.5, color = "black")
            self.axis[name][1].axvline(self.time[nperseg+20],alpha = 0.5, color = "black", label = "Window")
            self.axis[name][1].legend()
            self.axis[name][1].set_xlabel('Time [sec]')
    
    
            im1 = self.axis[name][0].pcolormesh(t, f, np.abs(Zxx))
            # self.axis[name][0].set_ylim(5e5, 10e6)
            # self.axis[name][0].set_yscale('log')
    
            self.axis[name][0].set_ylim(0, 4e6)
            self.axis[name][0].set_ylabel('Frequency [Hz]')
            self.axis[name][0].set_xlabel('Time [sec]')
    
            print(f'frequency resolution:  {f[1] / 1e6} MHz')
            if save:
                self.savefig(name)
    def continous_wavelet_trafo(self,nperfreq = 500, wavelet = 'morl', plot = False, save = False):

        paramdict = OrderedDict()
        paramdict["nperfreq"] = nperfreq
        paramdict["wavelet"] = wavelet
        paramdict["plot"] = plot
        paramdict["save"] = save


        self.log["function_calls"][f"continous_wavelet_trafo({argsstring(paramdict)})"] = paramdict


        # widths = np.logspace(1, 3.5, num = nperfreq)  # good setting
        widths = np.logspace(1, 3.3, num = nperfreq)

        # print(f"widths {widths}")
        # continuous_wavelets = ['mexh', 'morl', 'cgau5', 'gaus5']
        #
        # wavelet = 'morl'
        # wavelet = 'cmor1.0-2.0'

        # wavelet = 'cgau5'
        # wavelet = 'gaus5'
        # wavelet = 'mexh'

        cwtmatr, freqs = pywt.cwt(self.amplitude, widths, wavelet)
        cwtmatr = np.abs(cwtmatr)
        f = pywt.scale2frequency(wavelet, widths) * self.sr



        # wav = pywt.ContinuousWavelet('cmor1.5-1.0')
        wav = pywt.ContinuousWavelet(wavelet)

        prec = 1
        for i in range(2,30):
            int_psi, x = pywt.integrate_wavelet(wav, precision=i)

            if len(int_psi) > 1/4* len(self.time):
                prec = i
                # print(f'i{i}')
                break


        # print(f'lange time {1/4* len(self.time)}')
        int_psi, x = pywt.integrate_wavelet(wav, precision=prec)

        # print(f"lange morlet {len(int_psi)}")
        # print(f)
        # plt.figure()
        # plt.plot(f)
        # plt.yscale("log")
        # plt.figure()
        # plt.plot(int_psi)
        if plot:
            name = "cwt" + wavelet
            X, Y = np.meshgrid(self.time, f)

            self.figures[name], self.axis[name] = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            self.axis[name][1].plot(self.time, self.amplitude,alpha = 0.8)
            self.axis[name][1].plot(self.time[:len(int_psi)], int_psi/np.max(int_psi)*np.max(self.amplitude)-2*np.max(self.amplitude), label = wavelet)
    
            self.axis[name][1].legend()
    
            im1 = self.axis[name][0].pcolormesh(X, Y, np.abs(cwtmatr),shading='auto')
            # self.axis[name][0].set_ylim(5e5, 10e6)
            # self.axis[name][0].set_yscale('log')
    
            self.axis[name][0].set_ylim(0, 4e6)
            self.axis[name][0].set_ylabel('Frequency [Hz]')
            self.axis[name][0].set_xlabel('Time [sec]')
            self.axis[name][1].set_xlabel('Time [sec]')
            if save:
                self.savefig(name)

    def crosscorr(self,US_object, plot = False, save = False):

        #check if sampling rates are same
        assert self.sr  == US_object.sr, "crosscorr requires the same sampling rate"

        crosscorr = cross_correlation_using_fft(self.amplitude,US_object.amplitude)

        if plot:
            name = "crosscorr"
            self.figures[name], self.axis[name] = plt.subplots(3, 1, gridspec_kw={'height_ratios': [1, 1,2]})
            self.axis[name][0].plot(self.time, self.amplitude, label = "Pulse")
            self.axis[name][0].set_ylabel('Voltage [V]')
            self.axis[name][0].set_xlabel('Time [sec]')

            self.axis[name][1].plot(US_object.time, US_object.amplitude, label = "Pulse")
            self.axis[name][1].set_ylabel('Voltage [V]')
            self.axis[name][1].set_xlabel('Time [sec]')

            self.axis[name][2].plot(US_object.time - US_object.time[len(US_object.time)//2], crosscorr, label = "Crosscor")
            self.axis[name][2].set_ylabel('Crosscorr')
            self.axis[name][2].set_xlabel('Time [sec]')

            if save:
                self.savefig(name)






    def simple_plot(self):
        plt.figure("simple_plot")
        plt.plot(self.time,self.amplitude, label = "amplitude")
        plt.plot(self.time,self.envelope, label = "envelope")
        plt.legend(loc='upper left')
        plt.xlim(0,self.end_search_window)
        plt.scatter(self.time_max_amp, self.max_envelope, label="max_envelope")
    def plot_lukas_style(self,save = False):

        self.log["function_calls"][f"plot_lukas_style(save = {save})"] = {"save" : save}

        name = "lukas_style"
        self.figures[name], self.axis[name] = plt.subplots(1,2, gridspec_kw={'width_ratios': [2, 1]}, figsize = (16,9))

        self.axis[name][0].plot(self.time, self.amplitude, label="Signal")
        self.axis[name][0].plot(self.time, self.envelope, label="Envelope")
        self.axis[name][0].scatter(self.time_max_amp, self.max_envelope, label="max_envelope")
        self.axis[name][0].axvline(self.begin_noise, ls="--", alpha=0.5,color = "red")
        self.axis[name][0].axvline(self.end_noise, label="noise window", ls="--", alpha=0.5,color = "red")

        for key in self.toF_threshold_of_noises:
            self.axis[name][0].scatter(self.toF_threshold_of_noises[key][0], self.toF_threshold_of_noises[key][1]
                          , label="Thresh Noise " + key)
        for key in self.tof_threshold_of_amps:
            self.axis[name][0].scatter(self.tof_threshold_of_amps[key][0], self.tof_threshold_of_amps[key][1]
                          , label="Thresh amp " + key)

        if self.anawindow_left_time:
            self.axis[name][0].axvline(self.anawindow_right_time, label="spectral ana window", ls="--", alpha=0.5)
            self.axis[name][0].axvline(self.anawindow_left_time, ls="--", alpha=0.5)
        self.axis[name][0].legend()
        # freq, X = self.fourier_trafo(plot = False , low = 0, high =0)
        # self.axis[name][1].plot(freq, X , label=" Whole Signal")
        self.axis[name][1].set_xlim(0,0.4e7)
        if self.anawindow_left_time:
            freq, X = self.fourier_trafo(plot=False, low=self.anawindow_left_ind, high=self.anawindow_right_ind)
            freq_max, freq_left, freq_right, bandwidth_percent = bandwidth(freq, X, db=6, type="amplitude")

            self.axis[name][1].plot(freq, X , label="Signal Selection")



            self.axis[name][1].axvline(freq_left, label= str(round(freq_left/1e6,3)) + " MHz", ls="--", alpha=0.5)
            self.axis[name][1].axvline(freq_right, label= str(round(freq_right/1e6,3))+ " MHz", ls="--", alpha=0.5)
            self.axis[name][1].axvline(freq_max, label= str(round(freq_max/1e6,3))+ " MHz Center \nBandwidth: "
                                           + str(round((freq_right-freq_left)/2/freq_max*100,1)) + " %"
                                                 , ls="--", alpha=0.5, color = "r")
        self.axis[name][1].legend()

        if save:
            self.savefig(name)
        # self.toF_threshold_of_noises = {}
        # self.tof_threshold_of_amps = {}
        #
        # ax[0].scatter(self.time_max_amp, self.max_envelope, label="max_envelope")
        #
    def savefig(self, figname):
        results_directory = str(self.directory) + "/results"

        if not os.path.exists(results_directory):
            os.makedirs(results_directory)

        save_name = results_directory + "/"+figname + self.filename[-27:-6] + ".png"

        self.figures[figname].savefig(save_name)
        plt.close(self.figures[figname])


    def savelog(self,directory):

        with open((directory+'log.json'), 'w') as fp:
            json.dump(self.log, fp, indent=4)


if __name__ == "__main__":
    path = "C:/Users/feiler/Desktop/SP_059_USlong_1000cycles/"
    name = "SP_059_RPTlong_1000cycles_2022_04_27_23_53_51.ascan"



    path = "S:/spartacus/04_Arbeitspakete/02 WP2\Task 2.1 Acoustic measurement/PZT/03_Messdaten/Alterungsmessreihe/400cycles/SP_21_US_400cycle/"
    # name = "SP_UE059_2021_10_06_13_36_45.ascan"
    name = "SP_021_RPT_400Cycles_2022_01_17_11_08_40.ascan"
    # name = "SP_059_RPTlong_1000cycles_2022_04_29_21_26_22.ascan"



    # path = r"S:\spartacus\04_Arbeitspakete\02 WP2\Task 2.1 Acoustic measurement\PZT\03_Messdaten\Alterungsmessreihe\Initialer RPT_GITT_US_EIS\SP_21_US-2Messung/"
    # name = "SP_UE021_2021_10_25_16_31_34.ascan"
    #
    #
    # path = r"C:\Users\feiler\Desktop\Office_exp\Daten/"
    # path = r"\\wuestore.isc.loc\projekte\021_320\Mitarbeiter-in\Feiler\Messungen\M4L-Frequency-test\Office_exp\Daten/"
    # name = "M4L2022_05_06_10_00_45.ascan"


    # name =  "M4L2022_05_09_13_01_55.ascan"
    #--3
    # name = "M4L2022_05_09_10_49_28.ascan"  #ohne
    # name = "M4L2022_05_09_10_50_33.ascan"  # 0.5-2
    # # name = "M4L2022_05_09_10_51_20.ascan"  # 1.05-4
    # # name = "M4L2022_05_09_10_51_53.ascan"  #2.25-9
    #
    #- 4
    # name = "M4L2022_05_09_11_00_59.ascan"
    # name = "M4L2022_05_09_11_01_44.ascan"
    # name = "M4L2022_05_09_11_02_32.ascan"
    # name = "M4L2022_05_09_11_03_09.ascan"
    #
    #-Transmission
    # name = "M4L2022_05_09_11_11_22.ascan"
    # name = "M4L2022_05_09_11_11_55.ascan"
    # name = "M4L2022_05_09_11_12_26.ascan"
    # name = "M4L2022_05_09_11_12_48.ascan"

    #mit battery
    # name = "M4L2022_05_06_09_07_10.ascan"
    # name = "M4L2022_05_06_09_08_13.ascan"
    # name = "M4L2022_05_06_09_08_57.ascan"


    #1 Mhz
    #batter
    # name = "M4L2022_05_09_13_08_47.ascan"
    #no batt
    # name = "M4L2022_05_09_13_05_28.ascan"


    # path = r"C:\Users\feiler\Desktop\Office_exp\Daten/"
    #
    # name = "chirp_test_Ch_3_2022_05_09_17_54_47.ascan"
    # name = "chirp_test_Ch_3_2022_05_09_17_56_21.ascan"
    # name = "chirp_test_Ch_3_2022_05_09_17_57_24.ascan"
    # name = "chirp_test_Ch_3_2022_05_09_18_00_59.ascan"




    # name = "chirp_test_Ch_2_2022_05_09_17_42_13.ascan"
    # name = "chirp_test_Ch_3_2022_05_09_17_42_39.ascan"  # mit batery

    # name = "chirp_test_Ch_2_2022_05_09_17_47_12.ascan"
    # name = "chirp_test_Ch_3_2022_05_09_17_47_39.ascan"  # mit batery

    path = r"S:\spartacus\04_Arbeitspakete\02 WP2\Task 2.1 Acoustic measurement\PZT\03_Messdaten\Alterungsmessreihe\SP_027_Referenz\SP_027_US_0cycle/"
    # name = "SP_027_RPT_0cycles_2022_05_11_00_45_50.ascan"
    name = "SP_027_RPT_0cycles_2022_05_11_03_50_32.ascan"
    name = "SP_027_RPT_0cycles_2022_05_11_03_50_26.ascan"
    name = "SP_027_RPT_0cycles_2022_05_11_03_51_21.ascan"

    filename = path +name
    Spartacus = US_data_single_file_class(path,name,livedata = False, begin_noise=4e-6, end_noise=8e-6,
                 end_search_window =20e-6)

    Spartacus.detrend_amplitude()
    Spartacus.apply_Hamming_Window()
    # print(Spartacus.time_of_recording)
    # Spartacus.threshold_of_noise(1.5e-6,3.5e-6)
    # Spartacus.simple_plot()
    #
    tof_interp = Spartacus.ToF_threshold_of_noise(multiplicator=5)
    tof_interp = Spartacus.ToF_threshold_of_noise(multiplicator =10)
    tof_interp = Spartacus.ToF_threshold_of_noise(multiplicator =15)
    tof_interp = Spartacus.ToF_threshold_of_noise(multiplicator =20)


    tof_interp = Spartacus.ToF_threshold_of_amp(amp_frac=0.55)
    tof_interp = Spartacus.ToF_threshold_of_amp(amp_frac =0.5)
    tof_interp = Spartacus.ToF_threshold_of_amp(amp_frac =0.45)
    tof_interp = Spartacus.ToF_threshold_of_amp(amp_frac =0.2)
    tof_interp = Spartacus.ToF_threshold_of_amp(amp_frac =0.15)

    tof_interp = Spartacus.ToF_threshold_of_amp(amp_frac =0.1)
    tof_interp = Spartacus.ToF_threshold_of_amp(amp_frac =0.05)
    #


    # print(tof_interp)

    # plt.legend(loc='upper left')

    # Spartacus.downsample(2)

    cut_off_freq0 = 0.5e6
    cut_off_freq1 = 2e6
    cut_off_freq0 = 1.05e6
    cut_off_freq1 = 4e6

    # cut_off_freq0 = 0.9e6
    # cut_off_freq1 = 1.1e6
    stop_band_attenuation = 20
    roll_off_width = 1e6
    order = 5

    filter_type = "butter"
    # filter_type = "ellip"
    filter_type = "bessel"
    Spartacus.estimate_spectral_analysis_window(0.1,quick = False)


    # Spartacus.filter_amplitude(cut_off_freq0, cut_off_freq1, stop_band_attenuation, roll_off_width,True,save = True)
    # Spartacus.sos_filter_amplitude(filter_type,cut_off_freq0, cut_off_freq1, stop_band_attenuation,order,True,save = True)


    Spartacus.plot_lukas_style(save = False)

    ontinuous_wavelets = ['mexh', 'morl', 'cgau5', 'gaus5']
    #
    # wavelet = 'morl'
    # wavelet = 'cmor1.0-2.0'


    # Spartacus.short_time_fourier(time_intervall =4e-6,zeropadding = 2**3, overlap = 29/30,plot = True,save = False)


    # Spartacus.short_time_fourier(time_intervall =2.5e-6,zeropadding = 2**3, overlap = 59/60,plot = True,save = False)

    Spartacus.continous_wavelet_trafo(nperfreq = 500, wavelet = 'cmor3.0-1.5',plot = True,save = True)

    Spartacus.savelog(r"C:\Users\feiler\Desktop\test_dict_controll/")
    plt.show()

