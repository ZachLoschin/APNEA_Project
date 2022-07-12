# Import needed libraries
import numpy as np
import matplotlib.pyplot as plt
import mne
import scipy
from math import sqrt
import yasa
import seaborn as sns


import lightgbm
import antropy

"""
Function Definitions
"""

# Setup custom plot function
def my_plot(signalVec, timeVec, plotTitle):
  plt.plot()
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


def hypno_to_plot(hypno, artifactVec):
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
    print(len(hypno_enum))
    print(len(artifactVec))
    for j in range(len(hypno_enum)):
        for k in range(len(artifactVec[j])):
            print("Generating Graph...")
            if np.isnan(artifactVec[j][k]) == 1:
                #print("FOUND EVENT") this does print properly
                hypno_enum[j] = np.nan
                continue
    return hypno_enum

# Change filepath when submitting to cluster
filepath = '1.edf'

# Add a way to continue to next patient if there is an error
try:
    rawImport = mne.io.read_raw_edf(filepath, preload=True)
except:
    print("There was a problem reading in the data")


"""
Add keys to data dictionary
"""

# Create epoch vector
epochVec = create_epochs(rawImport["EEG"][0][0], rawImport.info["sfreq"], 30)

# Create epoch time vector
epochTimeVec = create_epochs(rawImport["EEG"][1], rawImport.info["sfreq"], 30)

# Create Dictionary for organization
data = create_dict(rawImport["EEG"][0][0], rawImport.info["sfreq"], rawImport["EEG"][1], epochVec, epochTimeVec)


"""
SET OUTLIERS TO ZERO

"""
threshold = 100 #uV

numberOfWindows = len(data["EEG"]) / (5*data["fs"])
windowsArray = np.array_split(data["EEG"], numberOfWindows)

for window in windowsArray:
    if max(abs(window)) >= threshold:
        for value in range(len(window)):
            window[value] = np.nan
            #window[value] = 0

data["EEG"] = np.concatenate(windowsArray)

data["EpochVecNan"] = create_epochs(data["EEG"], 256, 30)
"""
graphing hypnogram

"""

sls = yasa.SleepStaging(rawImport, eeg_name = "EEG")
sf = 256
# Get the predicted sleep stages
hypno = sls.predict()

#1 Get the predicted probabilities
proba = sls.predict_proba()
# Get the confidence
confidence = proba.max(axis=1)
# Plot the predicted probabilities
#sls.plot_predict_proba()
# Plot the hypnogram
#yasa.plot_spectrogram(data["EEG"], 256)
#hypno_to_plot(hypno)
#plt.show()


hypno_enum = hypno_to_plot(hypno, data["EpochVecNan"])
plt.plot(hypno_enum)
plt.title("Unfiltered Hypnogram: ", filepath)
plt.show()
