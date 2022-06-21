"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
6 June 2022
"""

"""
User made functions needed for running
of blocks in the cluster.
"""

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal


# Setup custom plot function
def my_plot(signalVec, timeVec, plotTitle, figureNumber):
  plt.figure(figureNumber)
  plt.plot(timeVec, signalVec)
  plt.title(plotTitle)
  plt.xlabel("Time (s)")
  plt.ylabel("Voltage (uV)")
  plt.show()


# Function to create Epochs
def create_epochs(signalVec, fs, epochLength):
  numberOfEpochs = len(signalVec) / (epochLength*fs)
  arrayOfEpochs = np.array_split(signalVec, numberOfEpochs)
  return arrayOfEpochs


# Function to create a dictionary for organization purposes
def create_dict(signalVec, fs, t, epochVec, epochTimeVec):
    data_dict = {'EEG': signalVec,
               'EpochVec': epochVec,
               'TimeVec': t,
               'EpochTimeVec': epochTimeVec,
               'fs': fs
               }
    return data_dict


def butter_bandpass(lowcut, highcut, fs, order=5):
    return scipy.signal.butter(order, [lowcut, highcut], fs=fs, btype='band')


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = scipy.signal.lfilter(b, a, data)
    return y

def hypno_to_plot_art(hypno):
    hypno_enum = []
    for i in range(len(hypno)):
        if hypno[i] =='W':
            hypno_enum.append(4)
        if hypno[i] == 'N1':
            hypno_enum.append(2)
        if hypno[i] == 'N2':
            hypno_enum.append(1)
        if hypno[i] == 'N3':
            hypno_enum.append(0)
        if hypno[i] == 'R':
            hypno_enum.append(3)
        if hypno[i] == 'U':
            hypno_enum.append(-2)
        if hypno[i] == 'A':
            hypno_enum.append(-1)
    return hypno_enum

def get_ID(file):
    filee = str(file)
    a = filee.split('\\')
    name = a[-1]
    aa = name.split('_')
    namee = aa[2]
    ID = int(namee[-3:-1] + (namee[-1]))
    return ID