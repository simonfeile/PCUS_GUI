import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.signal as sg
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-lukas-gold')
import helpfunctions as hf
# import read_ascan as read_as
import US_functions as us
import datetime

def US_ToF_ana(file_paths,resultpath):
    file_paths = hf.get_all_file_paths(data_path)
    file_paths.sort()
    file_paths = file_paths[:200]


    # print(file_paths[-1])

    ToF_threshold_of_amp = []
    datetime_format = []

    for i,file in enumerate(file_paths):
        # M4L-03-18_2021_08_13_12_01_11.ascan
        datetime_string = file[-25:-6]
        # 2021_08_13_12_01_11
        # print(datetime_string)
        time_datetimeformat = datetime.datetime.strptime(datetime_string, "%Y_%m_%d_%H_%M_%S")
        # print(time_datetimeformat)

        datetime_format.append(time_datetimeformat)
        ToF_threshold_of_amp.append(us.threshold_of_amp(file))
        if i%100 == 0:
            print(f'{round(i/len(file_paths)*100,1)}% done')

    d = {'ToF_threshold_of_amp': ToF_threshold_of_amp, 'datetime_format': datetime_format}
    df = pd.DataFrame(data=d)

    df.to_pickle(resultpath + "/ToF_threshold_of_amp.pkl")