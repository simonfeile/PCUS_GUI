import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.signal as sg
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-lukas-gold')
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-simon-feiler/US')
from collections import OrderedDict
import helpfunctions as hf
# import read_ascan as read_as
from helpfunctions import soc_calc
from helpfunctions import read_maccor_data
import US_functions as us
import datetime
import operator
import pandas as pd
from scipy.signal import savgol_filter
from pathlib import Path
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.colors as colors
# plt.close("all")

#
# rechteck  steel transmission -----------------------------------------------------
# with open('C:/Users/feiler/Desktop/Osci_test/Osci_TestUS_13_10_2021_14_29_58.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
# fs = 5 * 1e9
# nperseg = 2**13
# nfft_factor = 2**3
#
# # sine 5 cycl 4MHz  steel transmission -----------------------------------------------------
# with open('C:/Users/feiler/Desktop/Osci_test/Osci_TestUS_13_10_2021_16_05_11.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
# fs = 5 * 1e9
# nperseg = 2**13
# nfft_factor = 2**4

# #spartacus battery transmission -----------------------------------------------------
# with open('C:/Users/feiler/Desktop/Osci_test/Osci_TestUS_14_10_2021_17_59_29.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
# fs = 5 * 1e9
# nperseg = 2**13
# nfft_factor = 2**4
#
# # sine 10 cycl 4MHz  steel transmission -----------------------------------------------------
# with open('C:/Users/feiler/Desktop/Osci_test/Osci_TestUS_13_10_2021_16_16_40.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
# fs = 5 * 1e9
# nperseg = 2**15
# nfft_factor = 2**4

# # sine 5 cycl 2MHz  steel transmission -----------------------------------------------------
# with open('C:/Users/feiler/Desktop/Osci_test/Osci_TestUS_13_10_2021_16_20_24.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
# fs = 5 * 1e9
# nperseg = 2**13
# nfft_factor = 2**4
# sine 10 cycl 20MHz  steel transmission -----------------------------------------------------
# with open('C:/Users/feiler/Desktop/Osci_test/Osci_TestUS_13_10_2021_16_24_00.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
# fs = 5 * 1e9
# nperseg = 2**13
# nfft_factor = 2**4


#
# # Spartacus Transmission Batterie -----------------------------------------------------
data_path = Path(r"C:/Users/feiler/Desktop/SP_059_2Messung")
time,Amplitude_float =  us.amp_and_time(data_path/"SP_UE059_2021_10_06_22_49_38.ascan") # leer
# time,Amplitude_float =  us.amp_and_time(data_path/"SP_UE059_2021_10_09_09_03_18.ascan") # voll

fs = 100 * 1e6
nperseg = 2**7
nfft_factor = 2**3*nperseg


# # Spartacus Transmission  Steel-----------------------------------------------------
# data_path = Path(r"\\wuestore.isc.loc\projekte\021_320\Mitarbeiter-in\Daubinger\Spartacus\PZT_CEA_Leiterbahn")
# # time,Amplitude_float =  us.amp_and_time(data_path/"SP_UE059_2021_10_06_22_49_38.ascan") # leer
# time,Amplitude_float =  us.amp_and_time(data_path/"Pulse-Transmission-Steel.ascan") # voll
#
# fs = 100 * 1e6
# nperseg = 2**7
# nfft_factor = 2**3
#




# f, t, Zxx = signal.stft(Amplitude_float, fs,window='hann',padded=True,nfft = nperseg*4
#                         ,nperseg=nperseg,noverlap=nperseg-nperseg/16, boundary='zeros')

lowcut = 2e6
highcut = 2.5e6

width = 0.1e6
nyq = 0.5 * fs
ntaps = 2**11
atten = signal.kaiser_atten(ntaps, width / nyq)
beta = signal.kaiser_beta(atten)
taps = signal.firwin(ntaps, [lowcut, highcut], nyq=nyq, pass_zero=False,
              window=('kaiser', beta), scale=False)
plt.figure()
w, h = signal.freqz(taps, 1, worN=2000)
plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="Kaiser window, width=1.6")
plt.xlim(0,10e6)
# Amplitude_float = signal.filtfilt(taps, 1, Amplitude_float)


f, t, Zxx = signal.stft(Amplitude_float, fs,window='hann',nfft = nperseg*nfft_factor,nperseg=nperseg
                        ,noverlap=nperseg-nperseg/6)


# f, t, Zxx = signal.stft(Amplitude_float, fs,window='hann',nperseg=nperseg)
t = t + time[0]
# scipy.signal.stft(x, fs=1.0, window='hann', nperseg=256,
# noverlap=None, nfft=None, detrend=False, return_onesided=True, boundary='zeros', padded=True, axis=- 1)


maximum = np.max(np.abs(Zxx))
# plt.close("all")
fig, (a0, a1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex = True)
a1.plot(time,Amplitude_float)
a1.axvline(1e-5)
a1.axvline(time[nperseg]-time[0]+1e-5)

im1 = a0.pcolormesh(t, f, np.abs(Zxx))
# a0.pcolormesh(t, f, np.abs(Zxx),vmin=1e-6, norm=colors.LogNorm(), shading='gouraud')
# a0.pcolormesh(t, f, np.abs(Zxx),vmin=1e-4, norm=colors.LogNorm())
# a0.pcolormesh(t, f, np.abs(Zxx), norm=colors.LogNorm())
# a0.set_ylim(0,15e6)
a0.set_ylim(5e5,10e6)
a0.set_yscale('log')
a0.set_ylabel('Frequency [Hz]')
a0.set_xlabel('Time [sec]')




print(f'frequency resolution:  {f[1]/1e6} MHz')
plt.show()