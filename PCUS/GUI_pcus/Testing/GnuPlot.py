#tab size: 4, indent size: 4, keep tabs: yes

import clr

from System import Array, Object, Single

import subprocess

class GnuPlot(object):
	"""Gnuplot communication class"""

	def Create(self):
		self.__SubProcess = subprocess.Popen(['gnuplot','-p'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
		buf = "set terminal wxt noraise\n"
		self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.flush()
		buf = "set yrange [-1:1]\n"
		self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.flush()
		buf = "set mytics 4\n"
		self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.flush()
		buf = "set grid mytics\n"
		self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.flush()
		buf = "show grid\n"
		self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.flush()

	def Destroy(self):
		self.__SubProcess.stdin.write("quit\n")
		self.__SubProcess.stdin.flush()
		self.__SubProcess.kill()

	def SetYRange(self, Min, Max):
		buf = "set yrange [%f:%f]\n" % (Min, Max)
		self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.flush()
	
	def SetPlotLabel(self, label):
		buf = "set title \"%s\"\n" % label
		self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.flush()

	def PlotNetArray(self, Data, Name = ""):
		buf = "plot '-' with lines title \"%s\"\n" % Name
		self.__SubProcess.stdin.write(buf)
		
		for Element in range(0, Data.Length):
			buf = "%0.3f\n" % Data[Element]
			self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.write("eof\n")
		self.__SubProcess.stdin.flush()

	def PlotHorizontalLine(self, Start_X, Start_Y, End_X, End_Y):
		buf = "unset arrow\n"
		self.__SubProcess.stdin.write(buf)
		buf = "set arrow from %0.3f,%0.3f to %0.3f,%0.3f nohead filled back lw 1 lc rgb \"blue\"\n" % (Start_X, Start_Y, End_X, End_Y)
		self.__SubProcess.stdin.write(buf)
		buf = "refresh\n"
		self.__SubProcess.stdin.write(buf)
		self.__SubProcess.stdin.flush()