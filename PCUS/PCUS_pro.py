#tab size: 4, indent size: 4, keep tabs: yes

import clr
import os
import datetime
#load the LOCAL!!! Drivers dll, we have to use the absolute path, otherwise, the one from GAC will be used

clr.AddReference(os.getcwd() + "\\Fraunhofer.IKTS.Drivers.dll")

#clr.AddReference("Fraunhofer.IKTS.Drivers")
#clr.AddReference("System.Core.dll")

import ProgressHandler

from System.Collections.Generic import *
from System import Array, Object, Single
from abc import *
import numpy as np
from Fraunhofer.IKTS.Drivers import *
from Fraunhofer.IKTS.Drivers.Communication.Usb import DeviceLocatorFactory
from Fraunhofer.IKTS.Drivers.Communication import IDeviceLocator, IDeviceDescriptor
from Fraunhofer.IKTS.Drivers.Devices import * 
from Fraunhofer.IKTS.Drivers.Commands import *
from Fraunhofer.IKTS.Drivers.Commands.Backplane import * 
from Fraunhofer.IKTS.Drivers.Commands.Backplane import * 
from Fraunhofer.IKTS.Drivers.Commands.Channel import * 
from Fraunhofer.IKTS.Drivers.Commands.Channel import * 
from Fraunhofer.IKTS.Drivers.Devices.Channels.Configuration import * 
from Fraunhofer.IKTS.Drivers.Commands.VoltageSource import * 
from Fraunhofer.IKTS.Drivers import CommandFactory as CommandFactory

class PCUS_pro(object):
	"""PCUS pro communication class"""
	
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
		self.SampleRate = 100e6  # will be overwritten by device code bellow
		self.SpeedOfSound = 5920.0
		self.TriggerDelay = 0
		self.PreampEnabled = bool(False)
		self.DualInputMode = bool(False)

		self.ShotsToAverage = 10

		self.Mux = 1
		self.CompressionFactor = 1

		self.Channel = IUltraSoundChannel
		self.FilterData = FilterInformation
		self.FactoryData = IFactoryConfiguration
		
		self.SamplesStored = 0

		self.MaxSampleRate = 0
		self.WorkingChannel = 0
		self.MaxVoltage = 250.0
		self.MinVoltage = 50.0

		self.BackplaneVersion = 0
		self.BackplaneRevision = ""
		self.ChannelVersion = 0
		self.ChannelRevision = ""
		self.BackplaneBuildNumber = ""
		self.ChannelBuildNumber = ""

		self.__Backplane = IBackplane
		self.__Session = IMeasurementSession
		self.__ActiveChannel = List[IUltraSoundChannel]()
		self.__MeasSettings = IMeasurementSettings

	def SetGain(self,gain):
		print(f"Gain set to {gain}")
		self.Gain = gain
		self.ApplyMeasurementSettings()


	def GetGain(self):
		return self.Gain

	def SetImpulseLength(self,ImpulseLength):
		self.ImpulseLength = ImpulseLength
		self.ApplyMeasurementSettings()
		print(f"Impulse lenght = {ImpulseLength}")

	def GetImpulseLength(self):
		return self.ImpulseLength

	def SetImpulseVoltage(self,ImpulseVoltage):
		# print(f"set impulse voltage to {ImpulseVoltage}")
		if (ImpulseVoltage <= 250.0) & (ImpulseVoltage >= 50.0):
			self.ImpulseVoltage = ImpulseVoltage

		self.ApplyMeasurementSettings()

	def GetImpulseVoltage(self):
		return self.ImpulseVoltage

	def SetImpulseDelay(self,ImpulseDelay):
		"""
		takes impulse delay in us and converts to samples
		:param ImpulseDelay:
		:return:
		"""
		self.ImpulseDelay = ImpulseDelay *self.SampleRate*10e-6
		self.ApplyMeasurementSettings()

	def GetImpulseDelay(self):
		"""
		:return:
		float ImpulsDelay in us
		"""
		return self.ImpulseDelay / self.SampleRate / 10e-6

	def SetRecordingDelay(self,RecordingDelay):
		self.RecordingDelay = RecordingDelay *self.SampleRate*10e-6
		self.ApplyMeasurementSettings()

	def GetRecordingDelay(self):
		return self.RecordingDelay / self.SampleRate / 10e-6

	def SetRecordingLength(self,RecordingLength):
		"""
		takes recording length in us and converts to samples
		:param ImpulseDelay:
		:return:
		"""
		# print(f'RecordingLength {RecordingLength}')
		# print(f'self.SampleRate {self.SampleRate}')
		# print(f"Set Recording lenght in samples to {int(RecordingLength *self.SampleRate*1e-6)}")
		self.RecordingLength = int(RecordingLength *self.SampleRate*1e-6)
		self.ApplyMeasurementSettings()

	def GetRecordingLength(self):
		"""
		:return:
		float RecordingLength in us
		"""
		# print(f"self.RecordingLength {self.RecordingLength}")
		# print(f"self.SampleRate {self.SampleRate}")
		return self.RecordingLength / self.SampleRate /1e-6

	def SetFilter(self,Filter):
		self.Filter = Filter
		self.ApplyMeasurementSettings()

	def GetFilter(self):
		return self.Filter

	def SetPreampEnabled(self,PreampEnabled):
		print(f"PreampEnabled {PreampEnabled}")
		self.PreampEnabled = PreampEnabled
		self.ApplyMeasurementSettings()

	def GetPreampEnabled(self):
		return self.PreampEnabled


	def SetDualInputMode(self,DualInputMode):
		self.DualInputMode = DualInputMode
		self.ApplyMeasurementSettings()

	def GetDualInputMode(self):
		return self.DualInputMode

	def SetShotsToAverage(self,ShotsToAverage):
		self.ShotsToAverage = ShotsToAverage

	def GetShotsToAverage(self):
		return self.ShotsToAverage



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
		# print("settings from json written")
		# print(json.dumps(self.settings_dict, indent=4))


	def SearchAndOpenPCUSDevice(self):
		"""Searches for connected PCUS devices and let the user select one"""

		print("Scanning for connected PCUS...") 
		locator = DeviceLocatorFactory.Create()
		locator.Scan()
		
		print
		print("Found %d PCUS Devices" % (len(locator.Devices)))
		print


		if len(locator.Devices) == 0:
			raise Exception("No device found, Please make sure PCUS device is connected through USB and drivers are installed")


		for x in range (0, len(locator.Devices)):
			print("%d: %s" % (x, locator.Devices[x].Name))

		Device = 0
		# while True:
		# 	Device = input("Select Device index to open: [Enter for first, q for quit] ")
		#
		# 	if Device == "q": return -2
		#
		# 	if Device == "": Device = 0
		#
		# 	try:
		# 		Device = int(Device)
		# 		break
		# 	except ValueError:
		# 		print
		# 		print("Enter a valid device number.")
		# 		print

		if Device > (len(locator.Devices) - 1):
			print("Invalid device selection!")
			input("Press any key to exit")
			return -1

		BackplaneDescriptor = locator.Devices[Device]

		print("Connecting to Device %s..." % (Device),)

		Progress = ProgressHandler.PCUSProgressHandler()
		
		while True:
			try:
				self.__Backplane = BackplaneDescriptor.Connect(Progress)
				break
			except WindowsError as e:
				input("\nError opening PCUS pro : " + e.ToString() + "\nPress any key to continue")
				
		#os.system("cls")
		print("Connected.")

		self.MaxSampleRate = self.__Backplane.BaseFrequencyInHz
		self.SampleRate = self.MaxSampleRate
		
		self.BackplaneVersion = self.__Backplane.Version
		self.BackplaneRevision = self.__Backplane.HardwareRevision
		self.BackplaneBuildNumber = "%d.%d.%d.%d" % (self.__Backplane.FirmwareVersion.Major, 
													  self.__Backplane.FirmwareVersion.Commit,
													  self.__Backplane.FirmwareVersion.CommitCommon,
													  self.__Backplane.FirmwareVersion.Build)

		print("Opened %s" % (self.__Backplane.Name))
		print("Backplane Hardware Version: %04X" % (self.__Backplane.Version))
		print("Backplane Hardware Revision: %s" % (self.__Backplane.HardwareRevision))
		print("Firmware Revision: " + self.BackplaneBuildNumber)

		VoltageCommand = CommandFactory.CreateVoltageConfigurationCommand(self.__Backplane)

		ValueRestrictions = VoltageCommand.Restrictions
		ValueDescriptor = ValueRestrictions.GetValueDescriptor("VoltageInVolt")

		Voltages = ValueDescriptor.GetValues()
		
		if True == ValueDescriptor.IsFixedList():
			self.MaxVoltage = max(Voltages)
			self.MinVoltage = min(Voltages)
		elif True == ValueDescriptor.IsRange():
			
			self.MaxVoltage = Voltages[2]
			self.MinVoltage = Voltages[0]

		print("Minimum Transmitter Voltage: %0.0fV" % self.MinVoltage)
		print("Maximum Transmitter Voltage: %0.0fV" % self.MaxVoltage)

		return len(locator.Devices)
	
	def GetDeviceName(self):
		return self.__Backplane.Name

	def ClosePCUSDevice(self):
		"""Closes the connection to the PCUS pro device and dispose the resources"""
		self.__Backplane.Dispose()

	def ReadTemperature(self):
		"""Reads out the backplane temperature"""
		try:
			TempCmd = CommandFactory.CreateTemperatureReadCommand(self.__Backplane)
			self.__Backplane.Execute(TempCmd)
			return TempCmd.TemperatureInDegreeCelsius
		except AttributeError:
			print("Attribute Error in reading temperature!")
			return 0.0

	def SelectOneChannel(self, LastChannel):
		"""List all built in channels and let the user select one of it"""
		
		ChannelList = self.__Backplane.UltrasoundChannels

		print()
		while True:
			for self.Channel in ChannelList:
				self.FactoryData = self.Channel.FactorySettings
				print("Channel %d: Version: %04X, Serial: %s" % (self.Channel.Address, self.Channel.Version, self.FactoryData.SerialNumber))
		
			print
			if LastChannel != -1: print("Last selected channel was: %d" % LastChannel)
			if len(ChannelList) == 0:
				return -1

			if len(ChannelList) > 1:
				while True:
					try:
						Input = input("Select channel to activate or q for end ")
						if Input == "q":
							return -2
						self.WorkingChannel = int(Input)
						break
					except ValueError:
						print()
						print("Enter a valid number.")
						print()
			else: self.WorkingChannel = 0
			
			ChannelFound = False
			#store the factory and filter data into member variables
			for self.Channel in ChannelList:
				if self.WorkingChannel == self.Channel.Address:
					self.FactoryData = self.Channel.FactorySettings
					self.FilterData = self.FactoryData.FilterData
					self.ChannelVersion = self.Channel.Version
					self.ChannelRevision = self.Channel.HardwareRevision
					self.ChannelBuildNumber = "%d.%d.%d.%d" % (self.Channel.FirmwareVersion.Major, 
													  self.Channel.FirmwareVersion.Commit,
													  self.Channel.FirmwareVersion.CommitCommon,
													  self.Channel.FirmwareVersion.Build)
					ChannelFound = True
					break
			
			if ChannelFound == True: break
			else: print("Invalid Channel Selection")

		if ChannelFound == True:
			return self.WorkingChannel
		else:
			return -1
			
	def SelectOneChannelFUSE39A(self, ChannelToSet):
		"""Like SelectOneChannel, but does not show a list"""
		
		ChannelList = self.__Backplane.UltrasoundChannels
		self.WorkingChannel = ChannelToSet
		
		ChannelFound = False
		#store the factory and filter data into member variables
		for self.Channel in ChannelList:
			if self.WorkingChannel == self.Channel.Address:
				self.FactoryData = self.Channel.FactorySettings
				self.FilterData = self.FactoryData.FilterData
				self.ChannelVersion = self.Channel.Version
				self.ChannelRevision = self.Channel.HardwareRevision
				self.ChannelBuildNumber = "%d.%d.%d.%d" % (self.Channel.FirmwareVersion.Major, 
												  self.Channel.FirmwareVersion.Commit,
												  self.Channel.FirmwareVersion.CommitCommon,
												  self.Channel.FirmwareVersion.Build)
				ChannelFound = True
				break
		
		if ChannelFound == True:
			return self.WorkingChannel
		elif ChannelFound == False:
			print("Invalid Channel Selection")
			return -1
	
	def GetChannelList(self):
		"""Returns all built in channels"""
		
		return self.__Backplane.UltrasoundChannels		

	def WarmUp(self):
		"""Warm up the selected PCUS pro channel"""

		ChannelList = self.__Backplane.UltrasoundChannels

		for Channel in ChannelList:
			if Channel.Address == self.WorkingChannel:
				self.__ActiveChannel.Add(Channel)

		ChannelObject = Array.CreateInstance(Object, 1)
		ChannelObject[0] = self.__ActiveChannel

		WarmUpCommand = CommandFactory.CreateWarmupCommand(self.__Backplane, ChannelObject)
		self.__Backplane.Execute(WarmUpCommand)
	
	def WarmUpAllChannels(self):
		"""Warm up all PCUS pro channel"""

		WarmUpCommand = CommandFactory.CreateWarmupCommand(self.__Backplane, self.__Backplane.UltrasoundChannels)
		self.__Backplane.Execute(WarmUpCommand)
		

	def CoolDown(self):
		"""Cool down the selected PCUS pro channel"""

		CoolDownCommand = CommandFactory.CreateCooldownCommand(self.__Backplane, self.__ActiveChannel)
		self.__Backplane.Execute(CoolDownCommand)
	
	def CoolDownAllChannels(self):
		"""Cool down the selected PCUS pro channel"""

		CoolDownCommand = CommandFactory.CreateCooldownCommand(self.__Backplane, self.__Backplane.UltrasoundChannels)
		self.__Backplane.Execute(CoolDownCommand)

	def Reset(self):
		"""Reset the PCUS"""

		try:
			self.__Backplane.Reset()
		except Exception as e:
			print("Exception dureing reset: " + e)

	def ApplyMeasurementSettings(self):
		"""Set up the PCUS with the measurement settings for one channel only"""
		
		#Set up the backplane fixed trigger module
		TriggerCommand = CommandFactory.CreateFixedFrequencyTriggerCommand(self.__Backplane)
		TriggerCommand.TriggerFrequencyInHz = self.TriggerFrequency
		self.__Backplane.Execute(TriggerCommand)
		
		#set up the channel
		#self.__MeasSettings = CommandFactory.CreateMeasurementSettingsCommand(self.__Backplane, self.__ActiveChannel)

		SetupBatch = self.__Backplane.CreateCommand[IBatchedCommand]()

		NewChannelList = List[IUltraSoundChannel]()

		for Channel in self.__Backplane.UltrasoundChannels:
			
			if Channel.IsCommandSupported[IImpulseLengthConfigurationCommand]():
				ImpulseLengthCommand = Channel.CreateCommand[IImpulseLengthConfigurationCommand]()
				ImpulseLengthCommand.ImpulseLengthInNanoseconds = 0
				SetupBatch.AddCommand(ImpulseLengthCommand)

			if Channel.Address == self.WorkingChannel:
				NewChannelList.Add(Channel)

				if Channel.IsCommandSupported[IRecordingLengthConfigurationCommand]():
					LengthCommand = Channel.CreateCommand[IRecordingLengthConfigurationCommand]()
					LengthCommand.RecordingLengthInSamples = self.RecordingLength
					SetupBatch.AddCommand(LengthCommand)

				if Channel.IsCommandSupported[IRecordingDelayConfigurationCommand]():
					RecordingDelayCommand = Channel.CreateCommand[IRecordingDelayConfigurationCommand]()
					RecordingDelayCommand.RecordingDelayInNanoseconds = self.RecordingDelay
					SetupBatch.AddCommand(RecordingDelayCommand)

				if Channel.IsCommandSupported[IGainConfigurationCommand]():
					GainCommand = Channel.CreateCommand[IGainConfigurationCommand]()
					GainCommand.GainInDecibel = self.Gain
					self.Gain = GainCommand.GainInDecibel
					SetupBatch.AddCommand(GainCommand)

				if Channel.IsCommandSupported[ISampleRateConfigurationCommand]():
					SampleRateCommand = Channel.CreateCommand[ISampleRateConfigurationCommand]()
					SampleRateCommand.SampleRate = self.SampleRate
					SetupBatch.AddCommand(SampleRateCommand)

				if Channel.IsCommandSupported[IFilterConfigurationCommand]():
					FilterCommand = Channel.CreateCommand[IFilterConfigurationCommand]()
					FilterCommand.FilterIndex = self.Filter
					SetupBatch.AddCommand(FilterCommand)

				if Channel.IsCommandSupported[IReceiverMuxConfigurationCommand]():
					MuxCommand = Channel.CreateCommand[IReceiverMuxConfigurationCommand]()
					MuxCommand.Mux = self.Mux
					SetupBatch.AddCommand(MuxCommand)

				if Channel.IsCommandSupported[IInputModeConfigurationCommand]():
					InputModeCommand = Channel.CreateCommand[IInputModeConfigurationCommand]()
					if self.DualInputMode == True:
						InputModeCommand.InputMode = ChannelInputMode.SendReceive
					else:
						InputModeCommand.InputMode = ChannelInputMode.ImpulseEcho
					SetupBatch.AddCommand(InputModeCommand)

				if Channel.IsCommandSupported[IImpulseLengthConfigurationCommand]():
					ImpulseLengthCommand = Channel.CreateCommand[IImpulseLengthConfigurationCommand]()
					if self.Locked == False: ImpulseLengthCommand.ImpulseLengthInNanoseconds = self.ImpulseLength
					else: ImpulseLengthCommand.ImpulseLengthInNanoseconds = 0
					SetupBatch.AddCommand(ImpulseLengthCommand)

				if Channel.IsCommandSupported[IImpulseDelayConfigurationCommand]():
					ImpulseDelayCommand = Channel.CreateCommand[IImpulseDelayConfigurationCommand]()
					ImpulseDelayCommand.ImpulseDelayInNanoseconds = self.ImpulseDelay
					SetupBatch.AddCommand(ImpulseDelayCommand)

				if Channel.IsCommandSupported[ISenderConfigurationCommand]():
					SenderCommand = Channel.CreateCommand[ISenderConfigurationCommand]()
					if self.Locked == False: SenderCommand.EnableAllSenders()
					else: SenderCommand.DisableAllSenders()
					SetupBatch.AddCommand(SenderCommand)
				
				if Channel.IsCommandSupported[IMuxedImpulseDelayConfigurationCommand]():
					MuxDelayCommand = Channel.CreateCommand[IMuxedImpulseDelayConfigurationCommand]()
					for sender in range(MuxDelayCommand.NumberOfSenders):
						MuxDelayCommand.SetSenderImpulseDelay(sender , self.ImpulseDelay)
					SetupBatch.AddCommand(MuxDelayCommand)
				
				if Channel.IsCommandSupported[IPreamplifierConfigurationCommand]():
					PreampCommand = Channel.CreateCommand[IPreamplifierConfigurationCommand]()
					PreampCommand.PreamplifierEnabled = self.PreampEnabled
					SetupBatch.AddCommand(PreampCommand)
				
				if Channel.IsCommandSupported[ICompressionFactorConfigurationCommand]():
					#CompressionCommand = ICompressionFactorConfigurationCommand
					CompressionCommand = Channel.CreateCommand[ICompressionFactorConfigurationCommand]()
					CompressionCommand.CompressionFactor = self.CompressionFactor
					SetupBatch.AddCommand(CompressionCommand)

				if Channel.IsCommandSupported[IRectificationConfigurationCommand]():
					RectificationCommand = Channel.CreateCommand[IRectificationConfigurationCommand]()				
					if self.Rectification == "None":
						RectificationCommand.Rectification = 0
					elif self.Rectification == "PositiveHalf":
						RectificationCommand.Rectification = 1
					elif self.Rectification == "NegativeHalf":
						RectificationCommand.Rectification = 2
					elif self.Rectification == "Full":
						RectificationCommand.Rectification = 3
					else:
						RectificationCommand.Rectification = 0
				
					SetupBatch.AddCommand(RectificationCommand)

				try:
					self.__Backplane.Execute(SetupBatch)
				except Exception as error:
					print("Error while setup PCUS:")
					print(error)

		self.__Session = CommandFactory.CreateMeasurementSessionCommand(self.__Backplane, NewChannelList)
		
		VoltageCommand = CommandFactory.CreateIgnorePowerGoodVoltageConfigurationCommand(self.__Backplane)
		VoltageCommand.VoltageInVolt = self.ImpulseVoltage
		
		try:
			self.__Backplane.Execute(VoltageCommand)
		except Exception as error:
				print("Error while setup PCUS voltage: ")
				print(error)

	def ApplySettingsToAllChannels(self):
		
		#Set up the backplane fixed trigger module
		TriggerCommand = CommandFactory.CreateFixedFrequencyTriggerCommand(self.__Backplane)
		TriggerCommand.TriggerFrequencyInHz = self.TriggerFrequency
		self.__Backplane.Execute(TriggerCommand)
		
		SetupBatch = self.__Backplane.CreateCommand[IBatchedCommand]()

		for Channel in self.__Backplane.UltrasoundChannels:

			if Channel.IsCommandSupported[IRecordingLengthConfigurationCommand]():
				LengthCommand = Channel.CreateCommand[IRecordingLengthConfigurationCommand]()
				LengthCommand.RecordingLengthInSamples = self.RecordingLength
				SetupBatch.AddCommand(LengthCommand)

			if Channel.IsCommandSupported[IRecordingDelayConfigurationCommand]():
				RecordingDelayCommand = Channel.CreateCommand[IRecordingDelayConfigurationCommand]()
				RecordingDelayCommand.RecordingDelayInNanoseconds = self.RecordingDelay
				SetupBatch.AddCommand(RecordingDelayCommand)

			if Channel.IsCommandSupported[IGainConfigurationCommand]():
				GainCommand = Channel.CreateCommand[IGainConfigurationCommand]()
				GainCommand.GainInDecibel = self.Gain
				self.Gain = GainCommand.GainInDecibel
				SetupBatch.AddCommand(GainCommand)

			if Channel.IsCommandSupported[ISampleRateConfigurationCommand]():
				SampleRateCommand = Channel.CreateCommand[ISampleRateConfigurationCommand]()
				SampleRateCommand.SampleRate = self.SampleRate
				SetupBatch.AddCommand(SampleRateCommand)

			if Channel.IsCommandSupported[IFilterConfigurationCommand]():
				FilterCommand = Channel.CreateCommand[IFilterConfigurationCommand]()
				FilterCommand.FilterIndex = self.Filter
				SetupBatch.AddCommand(FilterCommand)

			if Channel.IsCommandSupported[IReceiverMuxConfigurationCommand]():
				MuxCommand = Channel.CreateCommand[IReceiverMuxConfigurationCommand]()
				MuxCommand.Mux = self.Mux
				SetupBatch.AddCommand(MuxCommand)

			if Channel.IsCommandSupported[IInputModeConfigurationCommand]():
				InputModeCommand = Channel.CreateCommand[IInputModeConfigurationCommand]()
				if self.DualInputMode == True:
					InputModeCommand.InputMode = ChannelInputMode.SendReceive
				else:
					InputModeCommand.InputMode = ChannelInputMode.ImpulseEcho
				SetupBatch.AddCommand(InputModeCommand)

			if Channel.IsCommandSupported[IImpulseLengthConfigurationCommand]():
				ImpulseLengthCommand = Channel.CreateCommand[IImpulseLengthConfigurationCommand]()
				if self.Locked == False: ImpulseLengthCommand.ImpulseLengthInNanoseconds = self.ImpulseLength
				else: ImpulseLengthCommand.ImpulseLengthInNanoseconds = 0
				SetupBatch.AddCommand(ImpulseLengthCommand)

			if Channel.IsCommandSupported[IImpulseDelayConfigurationCommand]():
				ImpulseDelayCommand = Channel.CreateCommand[IImpulseDelayConfigurationCommand]()
				ImpulseDelayCommand.ImpulseDelayInNanoseconds = self.ImpulseDelay
				SetupBatch.AddCommand(ImpulseDelayCommand)

			if Channel.IsCommandSupported[ISenderConfigurationCommand]():
				SenderCommand = Channel.CreateCommand[ISenderConfigurationCommand]()
				if self.Locked == False: SenderCommand.EnableAllSenders()
				else: SenderCommand.DisableAllSenders()
				SetupBatch.AddCommand(SenderCommand)
				
			if Channel.IsCommandSupported[IMuxedImpulseDelayConfigurationCommand]():
				MuxDelayCommand = Channel.CreateCommand[IMuxedImpulseDelayConfigurationCommand]()
				for sender in range(MuxDelayCommand.NumberOfSenders):
					MuxDelayCommand.SetSenderImpulseDelay(sender , self.ImpulseDelay)
				SetupBatch.AddCommand(MuxDelayCommand)
				
			if Channel.IsCommandSupported[IPreamplifierConfigurationCommand]():
				PreampCommand = Channel.CreateCommand[IPreamplifierConfigurationCommand]()
				PreampCommand.PreamplifierEnabled = self.PreampEnabled
				SetupBatch.AddCommand(PreampCommand)
			
			if Channel.IsCommandSupported[ICompressionFactorConfigurationCommand]():
					#CompressionCommand = ICompressionFactorConfigurationCommand
					CompressionCommand = Channel.CreateCommand[ICompressionFactorConfigurationCommand]()
					CompressionCommand.CompressionFactor = self.CompressionFactor
					SetupBatch.AddCommand(CompressionCommand)

			if Channel.IsCommandSupported[IRectificationConfigurationCommand]():
				RectificationCommand = Channel.CreateCommand[IRectificationConfigurationCommand]()				
				if self.Rectification == "None":
					RectificationCommand.Rectification = 0
				elif self.Rectification == "PositiveHalf":
					RectificationCommand.Rectification = 1
				elif self.Rectification == "NegativeHalf":
					RectificationCommand.Rectification = 2
				elif self.Rectification == "Full":
					RectificationCommand.Rectification = 3
				else:
					RectificationCommand.Rectification = 0
				
				SetupBatch.AddCommand(RectificationCommand)

			try:
				self.__Backplane.Execute(SetupBatch)
			except Exception as error:
				print("Error while setup PCUS: ")
				print(error)

		self.__Session = CommandFactory.CreateMeasurementSessionCommand(self.__Backplane, self.__Backplane.UltrasoundChannels)
		
		VoltageCommand = CommandFactory.CreateIgnorePowerGoodVoltageConfigurationCommand(self.__Backplane)
		VoltageCommand.VoltageInVolt = self.ImpulseVoltage
		try:
			self.__Backplane.Execute(VoltageCommand)
		except Exception as error:
				print("Error while setup PCUS voltage: ")
				print(error)

	def ExecuteMeasurement(self, ShotsToAverage):
		"""Perform the measurement(s) with Measurement settings"""
		# print(f"voltage for measurement : {self.ImpulseVoltage}")
		BatchCommand = CommandFactory.CreateBatchedCommand(self.__Backplane)

		Data = Array.CreateInstance(Single, self.RecordingLength)
		Array.Clear(Data, 0, Data.Length)

		Command = self.__Session

		for Shot in range(0, ShotsToAverage):
			BatchCommand.AddCommand(Command)
			Command = self.__Session.Clone()
		
		try:
			self.__Backplane.Execute(BatchCommand)
		except Exception as err:
			print("PCUS Exception: ")
			print(err)

		Session = IMeasurementSession
		ChannelSession = IChannelMeasurementSession

		Sessions = BatchCommand.GetCommands[IMeasurementSession]()

		try:
			for Session in Sessions:
				for ChannelSession in Session.Measurements:
					if ChannelSession.Channel.Address == self.WorkingChannel:
						SamplesStored = ChannelSession.Length
						if ShotsToAverage > 1:

							Temp = ChannelSession.GetSamples()
							for Sample in range(0, Temp.Length):
								Data[Sample] += Temp[Sample]
						else:
							Data = ChannelSession.GetSamples()
		except Exception as error:
			print("PCUS Exception: ")
			print(err)
		
		if ShotsToAverage > 1:
			for Sample in range(0, Data.Length):
				Data[Sample] /= float(ShotsToAverage)

		return Data #return the float array containing the shot data
		

	def ExecuteShots(self, Shots):
		"""Perform the measurement(s) with Measurement settings, shot only, not processing data"""
		
		BatchCommand = CommandFactory.CreateBatchedCommand(self.__Backplane)

		Data = Array.CreateInstance(Single, self.RecordingLength)
		Array.Clear(Data, 0, Data.Length)

		Command = self.__Session

		for Shot in range(0, Shots):
			BatchCommand.AddCommand(Command)
			Command = self.__Session.Clone()
		
		try:
			self.__Backplane.Execute(BatchCommand)
		except Exception as err:
			print("PCUS Exception:")
			print(err)

	def Snapsshot(self):
		"""Takes a measurement with specified averages

		returns
			np array of shot amplitude
		"""#
		dummy = self.ExecuteShots(1)  # somehow this is required to work
		data = self.ExecuteMeasurement(self.ShotsToAverage)
		dummy = self.ExecuteShots(1)  # somehow this is required to work

		completedata = []
		for Element in range(0, data.Length):
			# buf = "%0.3f\n" % data[Element]
			buf = data[Element]
			completedata.append(buf)
		completedata = np.array(completedata)
		# if list:
		completedata = list(completedata)
		return completedata

	def Save_shot_as_ascan(self, completedata, path, name):
		""" saves current shot as ascan"""
		settings_dict_pcus = self.get_current_settings_as_dict()  # these are the Measurement parameters set in PCUS

		now = datetime.datetime.now()
		date = str(now.strftime("%Y_%m_%d_%H_%M_%S"))
		filename = name + '_' + date + '.ascan'


		savename = path + '/' + filename

		with open(savename, 'w') as filehandle:
			for (key, value) in settings_dict_pcus.items():
				filehandle.write(str(key) + ': ' + str(value) + '\n')
			filehandle.write('\n')
			filehandle.write('ShotIndex;Amplitudes\n')
			for line in completedata:
				filehandle.write('%f;' % line)
		filehandle.close()

		# print(savename)
	def Snapshot_and_Save(self,path,name):
		"""
		executes Snapshot and saves at path with name + date
		:param path:
		:param name:
		:return:
		Amplitude
		"""
		completedata = list(self.Snapsshot())
		print("snapshot")

		self.Save_shot_as_ascan(completedata,path,name)

		print("save")
		return completedata

	def Snapshot_and_Save_with_spec_params(self, path, name, gain, impulselength, preamp, ):
		"""
		executes Snapshot and saves at path with name + date
		:param path:
		:param name:
		:return:
		Amplitude
		"""
		completedata = self.Snapshot_and_Save(self,path,name)



		return completedata





	def time_axis_for_current_measurement(self):
		"""returns time axis for current settings"""
		delay_in_us = self.GetRecordingDelay()
		recordinglength_in_us = self.GetRecordingLength()
		# time in mikro seconds
		time = np.linspace(0 + delay_in_us, delay_in_us + recordinglength_in_us, self.RecordingLength)
		return time

	def ConfigureDigitalFilterForWorkingChannel(self, HP_B0, HP_B1, HP_B2, HP_A1, HP_A2, LP_B0, LP_B1, LP_B2, LP_A1, LP_A2):
		
		for Channel in self.__Backplane.Channels:
			if Channel.ChannelIndex == self.WorkingChannel:
		
				command = CommandFactory.CreateDigitalFilterCommand(Channel)
				
				HighPass = DigitalIirFilterCoefficients
				
				HighPass.DenominatorA1 = HP_A1
				HighPass.DenominatorA2 = HP_A2
				HighPass.NumeratorB0 = HP_B0
				HighPass.NumeratorB1 = HP_B1
				HighPass.NumeratorB2 = HP_B2

				command.SetFirstBiquadCoefficients(HighPass)

				LowPass = DigitalIirFilterCoefficients

				LowPass.DenominatorA1 = LP_A1
				LowPass.DenominatorA2 = LP_A2
				LowPass.NumeratorB0 = LP_B0
				LowPass.NumeratorB1 = LP_B1
				LowPass.NumeratorB2 = LP_B2
				
				command.SetSecondBiquadCoefficients(LowPass)
				
				command.Active = True

				self.__Backplane.Execute(command)
				
	def SelectChannelRange(self, LastChannel_Start, LastChannel_End):
		"""List all built in channels and let the user select a range of it"""
		
		ChannelList = self.__Backplane.UltrasoundChannels

		print()
		for self.Channel in ChannelList:
			self.FactoryData = self.Channel.FactorySettings
			print("Channel %d: Version: %04X, Serial: %s" % (self.Channel.Address, self.Channel.Version, self.FactoryData.SerialNumber))
		
		print()
		if LastChannel_Start != -1: print("Last selected channel range was from %d to %d" % (LastChannel_Start, LastChannel_End))
		if len(ChannelList) == 0:
			return -1

		if len(ChannelList) > 1:
			while True:
				try:
					Input = input("Select channel address to start, a for all or q for quit ")
					if Input == "q":
						return (-2, -2)
					elif Input == "a":
						Channel_Start = self.__Backplane.UltrasoundChannels[0].Address
						Channel_End = self.__Backplane.UltrasoundChannels[len(self.__Backplane.UltrasoundChannels) - 1].Address
					else:
						Channel_Start = int(Input)
						Input = input("Select channel address to end or q for quit ")
						if Input == "q":
							return (-2, -2)
						else:
							Channel_End = int(Input)
					#self.WorkingChannel = int(Input)
					break
				except ValueError:
					print()
					print("Enter a valid number.")
					print()
		else: 
			Channel_Start = self.__Backplane.UltrasoundChannels[0].Address
			Channel_End = Channel_Start

		print("Range from address %d to %d" % (Channel_Start, Channel_End))
		return (Channel_Start, Channel_End)
		# TODO: Validate that all channels do exist