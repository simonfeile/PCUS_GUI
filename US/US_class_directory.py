import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import datetime
# from scipy.signal import savgol_filter
import pandas as pd
from US_data_single_file_class import US_data_single_file_class
import json
import pytz


def get_all_file_paths(directory,ending = ".ascan"):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            if ending in filename:
                # join the two strings in order to form the full file path.
                # file_path = os.path.join(root, filename)
                file_path = filename
                file_paths.append(file_path)

    # returning all the paths
    return file_paths

class US_measurement_class():
    """
    will contain a pandas df of us parameters
    """

    def __init__(self,directory,logfile_path,Startzeitpunkt_comb,custom_data = 0, start = datetime.datetime.now()-datetime.timedelta(hours =1e6) , end = datetime.datetime.now()):

        self.directory = directory
        self.Startzeitpunkt_comb = Startzeitpunkt_comb
        self.custom_data = custom_data
        self.file_paths = get_all_file_paths(directory)
        # self.file_paths = [r"Vorlaufkörper2022_03_21_09_21_09.ascan"]
        self.df = pd.DataFrame()
        self.start = start
        self.end = end



        with open(logfile_path) as json_file:
            self.log = json.load(json_file)

        self.read_files_to_df()

    # def eval_data_file(self):



    def read_files_to_df(self):


        init_key = list(self.log["__init__"].keys())[0]
        # print(self.log["__init__"][init_key])
        init_settings = self.log["__init__"][init_key]



        for i,file in enumerate(self.file_paths):
            if (i%100) ==0:
                print("reading in US " + str(round(i/len(self.file_paths),2)*100) + " % done")
            tempdf = pd.DataFrame()

            # initialize
            US_instance = US_data_single_file_class(directory=self.directory,
                                                    filename=file,
                                                    livedata=init_settings["livedata"],
                                                    begin_noise=init_settings["begin_noise"],
                                                    end_noise=init_settings["end_noise"],
                                                    end_search_window=init_settings["end_search_window"])

            #
            # if US_instance.time_of_recording < self.start or US_instance.time_of_recording > self.end:
            #     print("skip")
            #     continue

            # do all operations
            for j in self.log["function_calls"]:
                eval("US_instance." + j)

            if i == 0:
                results_directory = str(self.directory) + "/results/"

                if not os.path.exists(results_directory):
                    os.makedirs(results_directory)
                US_instance.savelog(results_directory)

            print(f"US_instance.time_of_recording {US_instance.time_of_recording}")
            time_of_recording = US_instance.time_of_recording

            # time_of_recording = time_of_recording.astimezone(pytz.utc)
            # time_of_recording = time_of_recording.replace(tzinfo=pytz.timezone('Europe/Berlin'))
            # time_of_recording = time_of_recording.astimezone(pytz.utc)

            tempdf['datetime'] = [time_of_recording]

            time = (round((time_of_recording - self.Startzeitpunkt_comb).days * 24 * 60 * 60
                              + (time_of_recording - self.Startzeitpunkt_comb).seconds
                              + (time_of_recording - self.Startzeitpunkt_comb).microseconds * 1e-6, 2))
            tempdf['time/s'] =[time]
            #dict


            for j in US_instance.tof_threshold_of_amps:
                tempdf['ToF_threshold_of_amp/µs'+j] = US_instance.tof_threshold_of_amps[j][0]


            for j in US_instance.toF_threshold_of_noises:
                tempdf['ToF_threshold_of_noise/µs'+j] = US_instance.toF_threshold_of_noises[j][0]


            tempdf['MaxAmp[a.u.]'] = [US_instance.max_envelope]
            tempdf['ToF_max_amp/µs'] = [US_instance.time_max_amp*1e6]

            if US_instance.anawindow_left_time:
                tempdf["Fmax/Hz"] = [US_instance.freq_max]
                tempdf["freq_left/Hz"] = [US_instance.freq_left]
                tempdf["freq_right/Hz"] = [US_instance.freq_right]
                tempdf["bandwidth/%"] = [US_instance.bandwidth_percent]

            if self.custom_data:
                for key in self.custom_data:
                    tempdf[key] = US_instance.log["params"][key]




            self.df = pd.concat([self.df, tempdf])

        return self.df

    def save_as_excel(self, filename):
        results_directory = str(self.directory) + "/results/"
        excel_path = results_directory + filename + "results.xlsx"
        self.df .to_excel(excel_path, index=False, header=True)



if __name__ == "__main__":
    directory = r"C:\Users\feiler\Desktop\test_dict_controll/2MHz/"
    logfile_path = r"C:\Users\feiler\Desktop\test_dict_controll\2MHz/log.json"
    datetime_string = "2022_02_18_14_16_39"
    Startzeitpunkt_comb = datetime.datetime.strptime(datetime_string, "%Y_%m_%d_%H_%M_%S")
    # Startzeitpunkt_comb.replace(tzinfo=pytz.timezone('Europe/Berlin'))

    customdata = ["FilterIndex","Gain [dB]","ImpulseVoltage [V]","ImpulseLength [ns]"]

    Ascan_Testing_GUI = US_measurement_class(directory,logfile_path,Startzeitpunkt_comb,customdata)
    asd = Ascan_Testing_GUI.df
    Ascan_Testing_GUI.save_as_excel("all")

    print(Ascan_Testing_GUI.df)
    # Ascan_Testing_GUI = US_measurement_class(directory,Startzeitpunkt_comb,begin_noise=3e-6, end_noise=5e-6,end_search_window = 16e-6, multiplicators = [5,10], amp_fracs = [0.05,0.1])


    plt.show()