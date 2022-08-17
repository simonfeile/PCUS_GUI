


class US_data_single_file_class():
    """
    container for single US_data file
    and analysis
    """

    def __init__(self):
        pass

    def filter_amplitude(self, cut_off_freq0):

        print(cut_off_freq0)
        type(cut_off_freq0)
        return



if __name__ == "__main__":

    Spartacus = US_data_single_file_class()


    cut_off_freq0 = 1.05e6
    cut_off_freq1 = 4e6

    stop_band_attenuation = 20
    roll_off_width = 1e6
    order = 5

    filter_type = "butter"
    # type = "ellip"
    type = "bessel"


    Spartacus.filter_amplitude(cut_off_freq0)
