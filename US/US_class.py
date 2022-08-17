import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import datetime
# from scipy.signal import savgol_filter
import pandas as pd
from US_data_single_file_class import US_data_single_file_class

import pytz


def get_all_file_paths(directory,ending = ".ascan"):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            if ending in filename:
                # join the two strings in order to form the full file path.
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)

    # returning all the paths
    return file_paths

class US_measurement_class():
    """
    will contain a pandas df of us parameters
    """

    def __init__(self,directory,Startzeitpunkt_comb,begin_noise, end_noise,end_search_window, multiplicators = [5,10], amp_fracs = [0.05,0.1], save = False):

        self.begin_noise = begin_noise
        self.end_noise = end_noise
        self.Startzeitpunkt_comb = Startzeitpunkt_comb
        self.multiplicators = multiplicators
        self.amp_fracs = amp_fracs
        self.end_search_window = end_search_window


        self.file_paths = get_all_file_paths(directory)


        self.save = save
        self.directory = directory
        # print(self.file_paths)

        self.read_files_to_df()


    def read_files_to_df(self):
        # print([str(round(amp_frac,3)) for amp_frac in self.amp_fracs])
        ToF_threshold_of_noise = {str(int(multiplicator)): []  for multiplicator in self.multiplicators}
        ToF_threshold_of_amp = {str(round(amp_frac,3)): []  for amp_frac in self.amp_fracs}

        ToF_max_amp = []
        datetime = []
        time = []
        max_envelope =[]

        for i,file in enumerate(self.file_paths):

            if (i%100) ==0:
                print("reading in US " + str(round(i/len(self.file_paths),2)*100) + " % done")

            if i == 0:
                US_instance = US_data_single_file_class(file,plot = True,livedata = False,begin_noise = self.begin_noise,
                                                        end_noise = self.end_noise ,end_search_window = self.end_search_window, save = self.save)
            else:
                US_instance = US_data_single_file_class(file,plot = False,livedata = False,begin_noise = self.begin_noise,
                                                        end_noise = self.end_noise ,end_search_window = self.end_search_window, save = self.save)

            time_of_recording = US_instance.time_of_recording

            # time_of_recording = time_of_recording.astimezone(pytz.utc)
            time_of_recording = time_of_recording.replace(tzinfo=pytz.timezone('Europe/Berlin'))
            # time_of_recording = time_of_recording.astimezone(pytz.utc)

            datetime.append(time_of_recording)
            time.append(round((time_of_recording - self.Startzeitpunkt_comb).days * 24 * 60 * 60
                              + (time_of_recording - self.Startzeitpunkt_comb).seconds
                              + (time_of_recording - self.Startzeitpunkt_comb).microseconds * 1e-6, 2))



            for multiplicator in self.multiplicators:
                ToF_threshold_of_noise[str(int(multiplicator))].append(US_instance.ToF_threshold_of_noise(multiplicator)*1e6)
            for amp_frac in self.amp_fracs:
                ToF_threshold_of_amp[str(round(amp_frac,3))].append(US_instance.ToF_threshold_of_amp(amp_frac)*1e6)

            max_envelope.append(US_instance.max_envelope)
            ToF_max_amp.append(US_instance.time_max_amp*1e6)

            if self.save:
                US_instance.savefig(self.directory)



        self.df = pd.DataFrame()
        self.df['time/s'] = time
        for multiplicator in self.multiplicators:
            self.df['ToF_threshold_of_noise/µs'+str(int(multiplicator))] = ToF_threshold_of_noise[str(int(multiplicator))]
        for amp_frac in self.amp_fracs:
            self.df['ToF_threshold_of_amp/µs' + str(round(amp_frac,3))] = ToF_threshold_of_amp[str(round(amp_frac,3))]

        self.df['ToF_max_amp/µs'] = ToF_max_amp
        self.df['datetime'] = datetime
        self.df['MaxAmp[a.u.]'] = max_envelope



        return self.df





if __name__ == "__main__":
    directory = "C:/Users/feiler/Desktop/Ascan_Testing_GUI/"
    datetime_string = "2022_02_18_14_16_39"
    Startzeitpunkt_comb = datetime.datetime.strptime(datetime_string, "%Y_%m_%d_%H_%M_%S")
    # Startzeitpunkt_comb.replace(tzinfo=pytz.timezone('Europe/Berlin'))
    Ascan_Testing_GUI = US_measurement_class(directory,Startzeitpunkt_comb,begin_noise=3e-6, end_noise=5e-6,end_search_window = 16e-6, multiplicators = [5,10], amp_fracs = [0.05,0.1])


    plt.show()