import clr
clr.AddReference("Fraunhofer.IKTS.Drivers")

from Fraunhofer.IKTS.Drivers.ComponentModel import *
import System

class PCUSProgressHandler(IProgressHandler):
	"""Progress handler for PCUS pro open operation"""
	__namespace__ = "MyNameSpace"		# https://stackoverflow.com/questions/49736531/implement-a-c-sharp-interface-in-python-for-net

	def ReportProgress(self, description, value, total):
		print(description)

	def get_IsCanceled(self):
		return False