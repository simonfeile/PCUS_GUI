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
import pywt
from matplotlib import ticker, cm
plt.close("all")

#
# rechteck  steel transmission -----------------------------------------------------
# with open('C:/Users/feiler/Desktop/Osci_test/Osci_TestUS_13_10_2021_14_29_58.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
# spartacus battery transmission -----------------------------------------------------
# with open('C:/Users/feiler/Desktop/Osci_test/Osci_TestUS_14_10_2021_17_59_29.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)



# 4 MHz prüfkopf auf prüfkopf -----------------------------------------------------
# with open('C:/Users/feiler/ownCloud/Messungen/Osci_versuche/prüfkopf_auf_prüfkopf/Osci_TestUS_20_10_2021_11_25_38.npy, 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
# # 4 MHz 50 cents -----------------------------------------------------
# with open('C:/Users/feiler/ownCloud/Messungen/Osci_versuche/50cents/Osci_TestUS_20_10_2021_11_33_16.npy', 'rb') as f:
#     time = np.load(f)
#     Amplitude_float = np.load(f)
#

#
# downscale = int(10)
# fs = 5 * 1e9 / downscale
# time = time[::downscale]
# Amplitude_float = Amplitude_float[::downscale]
# # max_width = 10000
# # widths = np.arange(0.1, max_width , 50)
# #
data_path = Path(r"C:\Users\feiler\Desktop\Office_exp\Daten/")

time,Amplitude_float =  us.amp_and_time(data_path/"M4L2022_05_09_11_11_22.ascan") # leer
# # time,Amplitude_float =  us.amp_and_time(data_path/"SP_UE059_2021_10_09_09_03_18.ascan") # voll

#
downscale = int(1)
fs = 100 * 1e6 / downscale
# time = time[::downscale]
Amplitude_float = Amplitude_float[::downscale]

max_width = 2000
widths = np.arange(0.1, max_width , 5)
###-----------------------filtering -----------------------------------

# #good
# lowcut = 1.6e6
# highcut = 2e6

#
# start = 12e-6
# end =20e-6
#
# Amplitude_float = Amplitude_float[(time>start) & (time<end)]
# time = time[(time>start) & (time<end)]
#

lowcut = 2e6
highcut = 2.5e6

lowcut = 1e6
highcut = 5e6

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


#############---------------------------------------CWT


fig, (a0, a1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex = True)
a1.plot(time,Amplitude_float)

continuous_wavelets = ['mexh', 'morl', 'cgau5', 'gaus5']

wavelet = 'morl'
# wavelet = 'mexh'

cwtmatr, freqs = pywt.cwt(Amplitude_float, widths, wavelet)
cwtmatr = np.abs(cwtmatr)
f = pywt.scale2frequency(wavelet, widths) * fs
#
#
# plt.figure()
# plt.imshow(cwtmatr, extent=[-1, 1, -1, max_width], cmap='PRGn', aspect='auto',
#             vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
# plt.colorbar()

lev_exp = np.arange(np.floor(np.log10(1e-1)-1),
                   np.ceil(np.log10(1)+1),0.2)
# lev_exp = np.arange(np.floor(np.log10(1e-1)-1),
#                    np.ceil(np.log10(1)+1),0.1)

levs = np.power(10, lev_exp)
X, Y = np.meshgrid(time, f)
# a0.contourf(X, Y, cwtmatr,locator=ticker.LogLocator())
cs = a0.contourf(X, Y, cwtmatr,levs,locator=ticker.LogLocator())
# cont = a0.contourf(X, Y, cwtmatr)
a0.set_ylim(6e5,10e6)



a0.set_yscale('log')
# fig.colorbar(cs)
plt.show()