import matplotlib.pyplot as plt # For ploting
import numpy as np # to work with numerical data efficiently

fs = 100 # sample rate 
f = 6 # the frequency of the signal

x = np.arange(fs) # the points on the x axis for plotting
# compute the value (amplitude) of the sin wave at the for each sample
# y = [ np.sin(2*np.pi*f * (i/fs)) for i in np.arange(fs)]

for x in range(fs):
        y = np.sin(2*np.pi*f * (float(x)/fs))
        cols = 40 - (30 * y)
        print " " * cols, "*"
        # print x,y

# % matplotlib inline
# # showing the exact location of the smaples
# plt.stem(x,y, 'r', )
# plt.plot(x,y)
