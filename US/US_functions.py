import sys
# import scipy.signal as sg
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-lukas-gold')
import helpfunctions as hf
import datetime
from scipy.interpolate import interp1d
import numpy as np
import scipy.signal as sg
import matplotlib.pyplot as plt
#
# from scipy.signal import savgol_filter
import pandas as pd


def amp_and_time(filename):
    """
    takes filename returns interpolated threshold_of_amp ToF
    :param filename:
    :return:
    """
    pcus_dict = hf.read_pcus_ascan(filename)
    Amplitudes = pcus_dict['Amplitudes']
    Amplitude_float = [float(amp) for amp in Amplitudes]
    Amplitude_float = np.array(Amplitude_float)

    sr = 100 * 1e6
    si = 1 / sr
    n_sa = len(Amplitude_float)
    delay = 4000 * 1e-9
    time = np.linspace(delay, delay + si * (n_sa - 1), num=n_sa)

    return time,Amplitude_float

def threshold_of_amp(filename):
    """
    takes filename returns interpolated threshold_of_amp ToF
    :param filename:
    :return:
    """
    pcus_dict = hf.read_pcus_ascan(filename)
    Amplitudes = pcus_dict['Amplitudes']
    Amplitude_float = [float(amp) for amp in Amplitudes]
    Amplitude_float = np.array(Amplitude_float)

    sr = 100 * 1e6
    si = 1 / sr
    n_sa = len(Amplitude_float)
    delay = 4000 * 1e-9
    time = np.linspace(delay, delay + si * (n_sa - 1), num=n_sa)

    analytical_signal_filt = sg.hilbert(Amplitude_float)
    envelope_filt = np.abs(analytical_signal_filt)

    envth_arg = np.argmax(envelope_filt > 0.05 * np.max(envelope_filt))
    if envth_arg < 3:
        envth_arg = 3
    envelope_filt_interp = envelope_filt[envth_arg - 2: envth_arg + 2]
    time_interp = time[envth_arg - 2: envth_arg + 2]

    time_fluent = np.linspace(time[envth_arg - 1], time[envth_arg + 1], 200, True)

    interpolation = interp1d(time_interp, envelope_filt_interp)

    envth_arg_interp = np.argmax(interpolation(time_fluent) > 0.05 * np.max(envelope_filt))

    tof_interp = time_fluent[envth_arg_interp]

    return tof_interp,0.05 * np.max(envelope_filt)


def threshold_of_noise(filename):
    """
    takes filename returns interpolated threshold_of_amp ToF
    :param filename:
    :return:
    """
    pcus_dict = hf.read_pcus_ascan(filename)
    Amplitudes = pcus_dict['Amplitudes']
    Amplitude_float = [float(amp) for amp in Amplitudes]
    Amplitude_float = np.array(Amplitude_float)

    sr = 100 * 1e6
    si = 1 / sr
    n_sa = len(Amplitude_float)
    delay = 4000 * 1e-9
    time = np.linspace(delay, delay + si * (n_sa - 1), num=n_sa)


    std_noise_threshhold =20 * np.std(Amplitude_float[200:800])
    envth_arg = np.argmax(Amplitude_float[200:] > std_noise_threshhold)+200 # 20 times noise
    if envth_arg < 3:
        envth_arg = 3

    envelope_filt_interp = Amplitude_float[envth_arg - 2: envth_arg + 2]
    time_interp = time[envth_arg - 2: envth_arg + 2]

    time_fluent = np.linspace(time[envth_arg - 1], time[envth_arg + 1], 200, True)

    interpolation = interp1d(time_interp, envelope_filt_interp)

    envth_arg_interp = np.argmax(interpolation(time_fluent) > std_noise_threshhold)

    tof_interp = time_fluent[envth_arg_interp]
    # print(tof_interp,std_noise_threshhold)

    # plt.figure()
    # plt.plot(time,Amplitude_float)
    # plt.axhline(std_noise_threshhold)
    # plt.scatter(time[envth_arg],std_noise_threshhold)
    return tof_interp,std_noise_threshhold






def plot(filename,savepath ="",save=False):
    '''
    takes acan filename and plots it
    :param filename:
    :return:
    '''
    pcus_dict = hf.read_pcus_ascan(filename)
    Amplitudes = pcus_dict['Amplitudes']
    Amplitude_float = [float(amp) for amp in Amplitudes]
    Amplitude_float = np.array(Amplitude_float)

    sr = 100 * 1e6
    si = 1 / sr
    n_sa = len(Amplitude_float)
    delay = 4000 * 1e-9
    time = np.linspace(delay, delay + si * (n_sa - 1), num=n_sa) * 1e6

    analytical_signal_filt = sg.hilbert(Amplitude_float)
    envelope_filt = np.abs(analytical_signal_filt)

    plt.figure()
    plt.plot(time, Amplitude_float,label = "Signal")
    plt.plot(time, envelope_filt, label = "Envelope")

    plt.xlabel("time[$\mu$s]")
    plt.ylabel("Amplitude")
    ToF_env, envmax = threshold_of_amp(filename)
    # plt.scatter(ToF_env*1e6, envmax,color ="red", label = "ToF 5% of max Envelope")
    ToF_std, envstd = threshold_of_noise(filename)
    plt.scatter(ToF_std*1e6, envstd,color ="green", label = "ToF 20 times Std",s=80)
    plt.legend()
    # print(savepath+"/"+filename[:-6]+".png")
    if save:
        plt.savefig(savepath+"/"+filename[-35:-6]+".png")
        plt.close()


def US_ToF_to_pickle(data_path,resultpath):
    file_paths = hf.get_all_file_paths(data_path)
    file_paths.sort()
    file_paths = file_paths[:-1]

    # file_paths = file_paths[-200:]
    print(file_paths[-1])

    ToF_threshold_of_amp = []
    ToF_threshold_std = []
    datetime_format = []

    for i,file in enumerate(file_paths):
        # M4L-03-18_2021_08_13_12_01_11.ascan
        datetime_string = file[-25:-6]
        # 2021_08_13_12_01_11
        # print(datetime_string)
        time_datetimeformat = datetime.datetime.strptime(datetime_string, "%Y_%m_%d_%H_%M_%S")
        # print(time_datetimeformat)

        datetime_format.append(time_datetimeformat)
        ToF_env, envmax = threshold_of_amp(file)
        ToF_threshold_of_amp.append(ToF_env)

        ToF_std, stdmax = threshold_of_noise(file)
        ToF_threshold_std.append(ToF_std)

        # print((resultpath+"/img"))
        # plot(file,(resultpath+"/img"),True)

        if i%100 == 0:
            print(f'{round(i/len(file_paths)*100,1)}% done')

    # ToF_threshold_of_amp = savgol_filter(ToF_threshold_of_amp, 51, 3)  # window size 51, polynomial order 3
    # ToF_threshold_std = savgol_filter(ToF_threshold_std, 51, 3)  # window size 51, polynomial order 3




    d = {'ToF_threshold_of_amp': ToF_threshold_of_amp,'ToF_threshold_std': ToF_threshold_std,
         'datetime_format': datetime_format}
    df = pd.DataFrame(data=d)

    df.to_pickle(resultpath / "ToF_threshold_of_amp.pkl")

if __name__ == "__main__":

    print("hello")