import numpy as np
from scipy import signal
from numpy.random import default_rng
import matplotlib.pyplot as plt

rng = default_rng()
npoints = 1000
noise = rng.standard_normal(npoints)
x = 3 + 8*np.linspace(0, 1, npoints) + noise
plt.figure()
plt.plot(signal.detrend(x))
plt.plot(x)
plt.show()


