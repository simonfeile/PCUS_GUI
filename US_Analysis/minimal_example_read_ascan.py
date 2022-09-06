import os
import matplotlib.pyplot as plt
import numpy as np

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
    ascan_file.close()

    #convert string Amplitudes to float
    ascan_dict["Amplitudes"] = [float(amp) for amp in ascan_dict["Amplitudes"]]

    return ascan_dict



if __name__ == "__main__":
    # get complete file path
    file_path = os.getcwd() + "/US_example_data/SP_021_RPT_400Cycles_2022_01_17_18_30_40.ascan"

    # apply read function
    ascan_dict = read_pcus_ascan(file_path)

    #create time axis
    delay = ascan_dict['RecordingDelay [us]'] * 1e-9
    n_sa = len(ascan_dict["Amplitudes"])
    si = 1 / (100 * 1e6) # sample rate is 100 MHz
    time = np.linspace(delay, delay + si * (n_sa - 1), num=n_sa)


    plt.figure()
    plt.plot(time,ascan_dict["Amplitudes"])
    plt.xlabel("time[s]")
    plt.ylabel("Amplitude")

