import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.signal as sg
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-lukas-gold')
import helpfunctions as hf
# import read_ascan as read_as

plt.close("all")

data_path = "C:/Users/feiler/Desktop/US-Analysis/US-Cycling"

file = "/M4L-03-15_2021_07_21_17_23_55.ascan"


file_paths = hf.get_all_file_paths(data_path)
file_paths.sort()


hf.combatOverflowError()

# print(file_paths[0])
pcus_dict = hf.read_pcus_ascan(data_path+file)

Amplitudes = pcus_dict['Amplitudes']
Amplitude_float = [float(amp) for amp in Amplitudes]
Amplitude_float = np.array(Amplitude_float)

sr  = 100 * 1e6
si = 1 / sr
n_sa = len(Amplitude_float)
delay = 4000 * 1e-9
time = np.linspace(delay, delay + si * (n_sa - 1), num=n_sa)

plt.figure()
plt.plot(time, Amplitude_float)


analytical_signal_filt = sg.hilbert(Amplitude_float)
envelope_filt = np.abs(analytical_signal_filt)

plt.plot(time, envelope_filt)
# plt.axhline(np.max(envelope_filt))
# plt.axhline(0.05*np.max(envelope_filt))

envth_arg = np.argmax(envelope_filt>0.05*np.max(envelope_filt))

plt.scatter(time[envth_arg], envelope_filt[envth_arg],s=30 , color = "g", label = "0.05 of max")

envelope_filt_interp = envelope_filt[envth_arg-2: envth_arg+2]
time_interp = time[envth_arg-2: envth_arg+2]

time_fluent = np.linspace(time[envth_arg-1], time[envth_arg+1], 200, True)

from scipy.interpolate import interp1d

interpolation = interp1d(time_interp, envelope_filt_interp)
plt.plot(time_fluent,interpolation(time_fluent), label = "interp")

envth_arg_interp = np.argmax(interpolation(time_fluent)>0.05*np.max(envelope_filt))

tof_interp = time_fluent[envth_arg_interp]

plt.scatter(time_fluent[envth_arg_interp], interpolation(time_fluent)[envth_arg_interp],s=30 , color = "r", label = "0.05 of max interp")

plt.legend()


print(time[envth_arg], envelope_filt[envth_arg])
plt.show()

