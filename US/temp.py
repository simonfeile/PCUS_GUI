
import sys
from scipy.interpolate import interp1d
import numpy as np
import scipy.signal as sg
import scipy.interpolate as sinter
import matplotlib.pyplot as plt
import datetime
import os
import sys
sys.path.append('C:/Users/feiler/gitlab/phd-thesis-simon-feiler/Math')
from FourierTrafo import FourierTransform
from FourierTrafo import Hamming_percentage
from FourierTrafo import bandwidth
from collections import OrderedDict
import pywt
from matplotlib import ticker, cm
dict = {"asd": 1.05e6}
#
# str = 1.05e6


print(type(str))



class US():
    def __init__(self):
        pass

    def filter_amplitude(self,cut_off_freq0):
        print(cut_off_freq0)
        print(type(cut_off_freq0))

if __name__ == "__main__":
    instance = US()
    cut_off_freq0 = 1.05e6
    instance.filter_amplitude(cut_off_freq0)




# var = dict["asd"]
#
# print(type(var))
#
# if str(type(dict["asd"])) == "<class 'str'>" :
#     print("is string")


