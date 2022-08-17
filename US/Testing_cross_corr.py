import datetime
import sys
import matplotlib.pyplot as plt
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-simon-feiler/Math')
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-simon-feiler/US')

from FourierTrafo import FourierTransform
from FourierTrafo import Hamming_percentage
from FourierTrafo import bandwidth
from US_data_single_file_class import US_data_single_file_class
from US_class_directory import US_measurement_class






if __name__ == "__main__":

    path = r"C:\Users\feiler\Desktop\test_dict_controll\Chirp_PMMA/"
    name_pulse = "chirp_test_Ch_2_2022_05_31_14_58_00.ascan"
    name_answer= "chirp_test_Ch_3_2022_05_31_14_58_00.ascan"

    filename = path +name_pulse
    Pulse = US_data_single_file_class(path,name_pulse,livedata = False, begin_noise=7e-6, end_noise=8e-6,
                 end_search_window =1000e-6)
    Pulse.detrend_amplitude()
    Pulse.apply_Hamming_Window()
    Pulse.downsample(25)
    cut_off_freq0 = 0.4e6
    # cut_off_freq1 = 2e6
    # cut_off_freq0 = 1.05e6
    cut_off_freq1 = 8e6
    # cut_off_freq0 = 0.9e6
    # cut_off_freq1 = 1.1e6
    stop_band_attenuation = 20
    roll_off_width = 1e6
    order = 1

    filter_type = "butter"
    # filter_type = "ellip"
    filter_type = "bessel"
    Pulse.estimate_spectral_analysis_window(0.1,quick = False)

    # Pulse.filter_amplitude(cut_off_freq0, cut_off_freq1, stop_band_attenuation, roll_off_width,True,save = True)
    Pulse.sos_filter_amplitude(filter_type,cut_off_freq0, cut_off_freq1, stop_band_attenuation,order,True,save = True)

    Pulse.plot_lukas_style(save = True)

    ontinuous_wavelets = ['mexh', 'morl', 'cgau5', 'gaus5']
    #
    # wavelet = 'morl'
    # wavelet = 'cmor1.0-2.0'
    # Pulse.short_time_fourier(time_intervall =4e-6,zeropadding = 2**3, overlap = 29/30,plot = True,save = False)
    # Pulse.short_time_fourier(time_intervall =10e-6,zeropadding = 2**3, overlap = 29/30,plot = True,save = False)

    Pulse.continous_wavelet_trafo(nperfreq = 500, wavelet = 'cmor1.5-1.5',plot = True,save = True)


    filename = path + name_answer
    Answer = US_data_single_file_class(path, name_answer, livedata=False, begin_noise=7e-6, end_noise=8e-6,
                                      end_search_window=1000e-6)


    Answer.detrend_amplitude()
    Answer.apply_Hamming_Window()
    Answer.downsample(25)
    Answer.estimate_spectral_analysis_window(0.1, quick=False)
    Answer.sos_filter_amplitude(filter_type, cut_off_freq0, cut_off_freq1, stop_band_attenuation, order, True, save=True)
    Answer.plot_lukas_style(save=True)
    Answer.continous_wavelet_trafo(nperfreq=500, wavelet='cmor1.5-1.5', plot=True, save=True)
    Pulse.crosscorr(Answer,True,True)
    Pulse.crosscorr(Answer,True,False)



    plt.show()