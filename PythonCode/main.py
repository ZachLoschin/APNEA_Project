# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
"""
Function Definitions
"""


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Import needed libraries
    import numpy as np
    import matplotlib.pyplot as plt
    import mne
    import scipy
    from math import sqrt
    from matplotlib.widgets import Slider

    # Change filepath when submitting to cluster
    filepath = 'S192.edf'

    # Add a way to continue to next patient if there is an error
    try:
        print("Importing Data")
        rawImport = mne.io.read_raw_edf(filepath, preload=True)
        print("Data Imported")
    except:
        print("There was a problem reading in the data")

    """
    Add keys to data dictionary
    """
    print("Creating Data Structure")

    # Create epoch vector
    epochVec = create_epochs(rawImport["EEG"][0][0], rawImport.info["sfreq"], 30)

    # Create epoch time vector
    epochTimeVec = create_epochs(rawImport["EEG"][1], rawImport.info["sfreq"], 30)

    # Create Dictionary for organization
    data = create_dict(rawImport["EEG"][0][0], rawImport.info["sfreq"], rawImport["EEG"][1], epochVec, epochTimeVec)

    # If the time and data vectors are not the same size, make new time vector
    if len(data["EEG"]) != len(data["TimeVec"]):
        t = []
        for i in range(len(data["EEG"])):
            t[i] = i * data["fs"]
        data["TimeVec"] = t

    """
    ALL VISUALIZATION FUNCTIONS WILL
    NEED TO BE REMOVED BEFORE WE
    SUBMIT TO THE HPC CLUSTER
    """

    # VISUALIZATION
    print("Creating Raw Data Plot")
    #my_plot(data["EEG"], data["TimeVec"], "Raw EEG Signal", 200)


    """
    Remove outliers and bandpass filter
    """
    print("Removing Outliers")
    threshold = 100  # uV

    numberOfWindows = len(data["EEG"]) / (5 * data["fs"])
    windowsArray = np.array_split(data["EEG"], numberOfWindows)

    for window in windowsArray:
        if max(abs(window)) >= threshold:
            for value in range(len(window)):
                window[value] = np.nan
    artifactRm = np.concatenate(windowsArray)

    print("Bandpass Filtering")
    for i in range(len(windowsArray)):
        windowsArray[i] = butter_bandpass_filter(windowsArray[i], 11, 15, rawImport.info["sfreq"], order=5)

    # windowsArray = butter_bandpass_filter(windowsArray, 11, 15, rawImport.info["sfreq"], order=5)

    data["EEG"] = np.concatenate(windowsArray)

    # VISUALIZATION
    print("Plotting Filtered Data")
    #my_plot(data["EEG"], data["TimeVec"], "EEG Signal with Large Amplitude Artifacts Removed and Filtered", 300)





    """
    PLOTTING WITH SLIDER
    """

    print("Creating Slider Plot")
    Plot, Axis = plt.subplots(2)

    plt.subplots_adjust(bottom=0.25)
    Axis[0].plot(data["TimeVec"], artifactRm)
    Axis[1].plot(data["TimeVec"], data["EEG"])

    # Choose the Slider color
    slider_color = 'White'

    # Set the axis and slider position in the plot
    axis_position = plt.axes([0.2, 0.1, 0.65, 0.03],
                             facecolor=slider_color)
    slider_position = Slider(axis_position,
                             'Pos', 0.1, 100000)

    # update() function to change the graph when the
    # slider is in use
    def update(val):
        pos = slider_position.val
        Axis[0].axis([pos, pos + 30, -1, 1])
        Axis[1].axis([pos, pos + 30, -1, 1])
        Plot.canvas.draw_idle()
        plt.ylim([-30,30])
        Axis[0].set_ylim([-100, 100])
        Axis[1].set_ylim([-30, 30])



    # update function called using on_changed() function
    slider_position.on_changed(update)

    # Display the plot
    plt.ylim([-30,30])
    plt.show()