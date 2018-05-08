# coding = utf-8

import os
import requests
import json
import time
import traceback
import matplotlib.pyplot as plt
import numpy as np
from pylab import mpl
from scipy.interpolate import spline
from datetime import datetime

import matplotlib.dates as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

X = np.linspace(-15, 15, 3)
Y = np.sinc(X)

ax = plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

plt.plot(X, Y, c = 'k')
plt.show()