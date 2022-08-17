import numpy as np





class PCUS_dummy(object):
    """PCUS pro dummy communication class"""

    def __init__(self):
        self.TriggerFrequency = 100
        self.Filter = 0
        self.Gain = 0.0
        self.ImpulseDelay = float(0)
        self.ImpulseLength = 50.0
        self.ImpulseVoltage = 180.0
        self.Locked = False
        self.RecordingDelay = 0.0
        self.RecordingLength = 2000
        self.ProbeDelay = 0
        self.Rectification = "None"
        self.SampleRate = 100e6
        self.SpeedOfSound = 5920.0
        self.TriggerDelay = 0
        self.PreampEnabled = bool(False)
        self.DualInputMode = bool(False)

        self.ShotsToAverage = 10

        self.Mux = 1
        self.CompressionFactor = 1

        self.SamplesStored = 0

        self.MaxSampleRate = 0
        self.WorkingChannel = 0
        self.MaxVoltage = 250.0
        self.MinVoltage = 50.0

        x = x = np.linspace(0,20,1000)
        self.dummy_signal = 0.5*np.exp(-(x - 5) ** 2 / 2) * np.cos(x * 10)



    def SetGain(self, gain):
        print(f"Gain set to {gain}")
        self.Gain = gain
        self.ApplyMeasurementSettings()

    def GetGain(self):
        return self.Gain

    def SetImpulseLength(self, ImpulseLength):
        self.ImpulseLength = ImpulseLength
        self.ApplyMeasurementSettings()
        print(f"Impulse lenght = {ImpulseLength}")

    def GetImpulseLength(self):
        return self.ImpulseLength

    def SetImpulseVoltage(self, ImpulseVoltage):
        # print(f"set impulse voltage to {ImpulseVoltage}")
        if (ImpulseVoltage <= 250.0) & (ImpulseVoltage >= 50.0):
            self.ImpulseVoltage = ImpulseVoltage

        self.ApplyMeasurementSettings()

    def GetImpulseVoltage(self):
        return self.ImpulseVoltage

    def SetImpulseDelay(self, ImpulseDelay):
        """
        takes impulse delay in us and converts to samples
        :param ImpulseDelay:
        :return:
        """
        self.ImpulseDelay = ImpulseDelay * self.SampleRate * 10e-6
        self.ApplyMeasurementSettings()

    def GetImpulseDelay(self):
        """
        :return:
        float ImpulsDelay in us
        """
        return self.ImpulseDelay / self.SampleRate / 10e-6

    def SetRecordingDelay(self, RecordingDelay):
        self.RecordingDelay = RecordingDelay * self.SampleRate * 10e-6
        self.ApplyMeasurementSettings()

    def GetRecordingDelay(self):
        return self.RecordingDelay / self.SampleRate / 10e-6

    def SetRecordingLength(self, RecordingLength):
        """
        takes recording length in us and converts to samples
        :param ImpulseDelay:
        :return:
        """
        self.RecordingLength = int(RecordingLength * self.SampleRate * 1e-6)
        self.ApplyMeasurementSettings()

    def GetRecordingLength(self):
        """
        :return:
        float RecordingLength in us
        """

        # print(f"self.RecordingLength {self.RecordingLength}")
        # print(f"self.SampleRate {self.SampleRate}")

        return self.RecordingLength / self.SampleRate / 1e-6

    def SetFilter(self, Filter):
        self.Filter = Filter
        self.ApplyMeasurementSettings()

    def GetFilter(self):
        return self.Filter

    def SetPreampEnabled(self, PreampEnabled):
        print(f"PreampEnabled {PreampEnabled}")
        self.PreampEnabled = PreampEnabled
        self.ApplyMeasurementSettings()

    def GetPreampEnabled(self):
        return self.PreampEnabled

    def SetDualInputMode(self, DualInputMode):
        self.DualInputMode = DualInputMode
        self.ApplyMeasurementSettings()

    def GetDualInputMode(self):
        return self.DualInputMode


    def SetShotsToAverage(self, ShotsToAverage):
        self.ShotsToAverage = ShotsToAverage

    def GetShotsToAverage(self):
        return self.ShotsToAverage

    def Snapshot_and_Save(self, path, name):
        print(f'path : {path}')
        print(f'name : {name}')
        noise = np.random.normal(0, 0.05, 1000)
        completedata = list(self.dummy_signal+noise)

        print("dummy device didnt save file")
        return completedata


    def Snapsshot(self):
        print("snap")
        noise = np.random.normal(0, 0.05, 1000)
        completedata = list(self.dummy_signal+noise)
        return completedata

    def SearchAndOpenPCUSDevice(self):
        print("found dummy device")
        return

    def WarmUpAllChannels(self):
        print("dummy device is warmed up")
        return

    def ClosePCUSDevice(self):
        print("dummy device closed")
        return

    def set_settings_from_dict(self,settings_dict):
        self.SetImpulseLength(settings_dict["ImpulseLength [ns]"])
        self.SetImpulseVoltage(settings_dict["ImpulseVoltage [V]"])
        self.SetImpulseDelay(settings_dict["ImpulseDelay [us]"])
        self.SetRecordingDelay(settings_dict["RecordingDelay [us]"])
        self.SetRecordingLength(settings_dict["RecordingLength [us]"])
        self.SetGain(settings_dict["Gain [dB]"])
        self.SetFilter(settings_dict["FilterIndex"])
        self.SetPreampEnabled(settings_dict["Preamplifier enabled"])
        self.SetDualInputMode(settings_dict["DualInputMode"])
        self.SetShotsToAverage(settings_dict["Averages"])
        self.ApplyMeasurementSettings()


    def get_current_settings_as_dict(self):
        settings_dict = \
            {
                "ImpulseLength [ns]": self.GetImpulseLength(),
                "ImpulseVoltage [V]": self.GetImpulseVoltage(),
                "ImpulseDelay [us]": self.GetImpulseDelay(),  # from µs to samples
                "RecordingDelay [us]": self.GetRecordingDelay(),  # from µs to samples
                "RecordingLength [us]": self.GetRecordingLength(),  # from µs to samples
                "Gain [dB]": self.GetGain(),
                "FilterIndex": self.GetFilter(),
                "Preamplifier enabled": self.GetPreampEnabled(),
                "DualInputMode": self.GetDualInputMode(),
                "Averages": self.GetShotsToAverage()
            }
        # print(json.dumps(self.settings_dict, indent=4))
        return settings_dict

    def ApplyMeasurementSettings(self):
        return