import os
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pandas as pd
from US_data_single_file_analysis import US_data_single_file_class


def get_all_file_paths(directory,ending = ".ascan"):
    # initializing empty file paths list
    file_paths = []
    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory, topdown=True):
        for filename in files:
            if ending in filename:
                # join the two strings in order to form the full file path.
                # file_path = os.path.join(root, filename)
                file_path = filename
                file_paths.append(directory + "/" + file_path)

    # returning all the paths
    return sorted(file_paths)

class US_measurement_class():
    """
    will contain a pandas df of us parameters
    """

    def __init__(self,directory, amp_treshhold, Startzeitpunkt_comb = 0):
        """
        :param filename: full path of US file to be analysed
        :param amp_treshhold: threshhold of amplitude
        """

        self.directory = directory
        self.Startzeitpunkt_comb = Startzeitpunkt_comb
        self.amp_treshhold = amp_treshhold
        self.file_paths = get_all_file_paths(directory)
        print(self.file_paths)

        self.df = pd.DataFrame()

        self.read_files_to_df()


    def read_files_to_df(self):

        for i, file in enumerate(self.file_paths):
            if (i % 100) == 0:
                print("reading in US " + str(round(i / len(self.file_paths), 2) * 100) + " % done")
            tempdf = pd.DataFrame()
            # initialize
            US_instance = US_data_single_file_class(file,self.amp_treshhold)
            time_of_recording = US_instance.time_of_recording

            # set time of recording of first file to 0 s
            if i == 0:
                # if no start time is provided the first file's is used
                if self.Startzeitpunkt_comb == 0:
                        self.Startzeitpunkt_comb = time_of_recording
                print(f"Start of time set to {self.Startzeitpunkt_comb}")

            tempdf['datetime'] = [time_of_recording]

            time = (round((time_of_recording - self.Startzeitpunkt_comb).days * 24 * 60 * 60
                              + (time_of_recording - self.Startzeitpunkt_comb).seconds
                              + (time_of_recording - self.Startzeitpunkt_comb).microseconds * 1e-6, 2))
            tempdf['time/s'] =[time]

            tempdf['ToF_threshold_of_amp/µs'] = US_instance.tof_threshold_of_amp * 1e6

            tempdf['MaxAmp[a.u.]'] = [US_instance.max_envelope]

            tempdf['ToF_max_amp/µs'] = [US_instance.time_max_amp * 1e6]

            self.df = pd.concat([self.df, tempdf]) # memory inefficient but easy

        self.df = self.df.sort_values(by = ['time/s'])

        print(self.df)


    def simple_plot(self):
        fig, ax = plt.subplots(3,sharex = True)
        ax[0].plot(self.df['time/s'], self.df['ToF_threshold_of_amp/µs'])
        ax[0].set_ylabel('ToF_threshold_of_amp[µs]')
        ax[1].plot(self.df['time/s'], self.df['ToF_max_amp/µs'])
        ax[1].set_ylabel('ToF_max_amp[µs]')
        ax[2].plot(self.df ['time/s'], self.df ['MaxAmp[a.u.]'])
        ax[2].set_ylabel('MaxAmp[a.u.]')
        ax[2].set_xlabel("time[s]")


    def save_df_as_csv(self,name):

        # create results folder
        results_directory = str(self.directory) + "/results/"

        if not os.path.exists(results_directory):
            os.makedirs(results_directory)

        self.df.to_csv(str(self.directory) + "/results/" + name + ".csv", index = False)

    def save_df_as_excel(self,name):
        # create results folder

        results_directory = str(self.directory) + "/results/"
        if not os.path.exists(results_directory):
            os.makedirs(results_directory)

        self.df.to_excel(str(self.directory) + "/results/" + name + ".xlsx", index = False)




if __name__ == "__main__":

    # get complete file path
    file_path = os.getcwd() + "/US_example_data"

    # chose amp threshhold
    amp_threshhold = 0.1

    # set manual start time
    start_time = datetime.datetime.strptime("2022-01-17 18:20:40", '%Y-%m-%d %H:%M:%S')

    # set automatic (first US file (as sorted by windows/alphabetically)) as starttime
    start_time = 0

    # create instance
    US_measurement_multiple = US_measurement_class(file_path,amp_threshhold)
    # plot
    US_measurement_multiple.simple_plot()

    # save as excel
    US_measurement_multiple.save_df_as_excel("results_as_excel")
    # save as csv
    US_measurement_multiple.save_df_as_csv("results_as_csv")

    plt.show()