import clr

from PCUS_pro import *

import GnuPlot

import matplotlib.pyplot as plt

pcus = PCUS_pro()

pcus.SearchAndOpenPCUSDevice()
#
# Channel = pcus.SelectOneChannel(-1)

pcus.WarmUpAllChannels()

pcus.ApplyMeasurementSettings()

data = pcus.ExecuteMeasurement(20)

# Plot = GnuPlot.GnuPlot()

# Plot.Create()
# Plot.SetYRange(-1, 1)

# Plot.PlotNetArray(data)

# input("")

# Plot.Destroy()
completedata = []
for Element in range(0, data.Length):
    # buf = "%0.3f\n" % data[Element]
    buf = data[Element]
    completedata.append(buf)

plt.figure()
plt.plot(completedata)

print(completedata)
pcus.ClosePCUSDevice()

plt.show()