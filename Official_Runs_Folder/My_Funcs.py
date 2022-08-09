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
import pandas as pd
import yasa
import mne

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


def detect_spindles(data, hypnoEnum, night, samples1):
    """
    3) Yasa spindle detection
    """
    print("Detecting spindles...")
    thresh = {'rel_pow': None, 'corr': None, 'rms': 2}
    # TRY THE EPOCHED DATA HERE INSTEAD
    sp = yasa.spindles_detect(data["EEG_ArtZero"], data["fs"], ch_names=['EEG'],
                              freq_sp=(9, 15), thresh=thresh)

    """
    4) Learn the spindle object
    """
    print("Creating spindle dataframe...")
    summary = sp.summary()
    summary = pd.DataFrame(summary)

    print("Removing everything but spindles...")
    # Create vector of zeros, set spindle areas to 1
    data["Spindle_Vec"] = np.empty(len(data["TimeVec"]))
    data["Spindle_Vec"][:] = np.nan

    count = 0

    # Create lists for noise
    Beta_Noise = np.ones(len(summary))
    Art_Noise = np.zeros(len(summary))

    # Create vector to hold the sleep state of each spindle
    spindleStates = []
    hypnoBySecond = np.repeat(hypnoEnum, 30)
    print(len(hypnoBySecond))

    # If night 1, index the hypnogram from the front
    # If night 2, start indexing the hypnogram from where night 2 starts
    for index, row in summary.iterrows():
        start = int(row['Start'] * data['fs'])
        end = int(row["End"] * data['fs'])

        # The hypnoBySecond has one state per second. So if we input the time of the spindle -1 to account for
        # base zero indexing, the state at this index of hypnoBySecond will bet the state the spindle is in

        if night == 1:
            try:
                state = hypnoBySecond[round(row["Start"]) - 1]
                spindleStates.append(state)
            except:
                state = -1
                spindleStates.append(state)
        else:
            try:
                night2_start_seconds = samples1 / 256
                state = hypnoBySecond[round(night2_start_seconds + row["Start"]) - 1]
                spindleStates.append(state)
            except:
                state = -1
                spindleStates.append(state)

        # If there are no beta or threshold artifacts within the spindle range
        if sum(data["Beta_Labels"][start:end]) == 0:  # and np.isnan(sum(data["ArtZero"][start:end])) is False:
            data["Spindle_Vec"][start:end] = 20
            data["Spindle_Vec"][start - 1] = 0
            data["Spindle_Vec"][end + 1] = 0

        count = count+1
        print("Spindles set: %d" % count)

    # Add the states to the summary vector
    summary["State"] = spindleStates

    # # Remove the spindles with beta noise marked as 1
    for i in range(len(Beta_Noise)):
        start = int(summary['Start'][i] * data['fs'])
        end = int(summary["End"][i] * data['fs'])

        # If there are no beta arts within spindle range
        if sum(data["Beta_Labels"][start:end]) == 0:
            Beta_Noise[i] = 0  # Set the noize vectors properly

        # If there is thresh art in the spindle range
        if np.isnan(sum(data["ArtZero"][start:end])):
            Art_Noise[i] = 1  # Set the noize vectors properly

    # Add the noise vectors to the DataFrame
    summary["Beta_Noise"] = Beta_Noise
    summary["Art_Noise"] = Art_Noise

    # Filter by no noise spindles
    summary = summary.loc[summary["Beta_Noise"] == 0]
    summary = summary.loc[summary["Art_Noise"] == 0]

    return summary


def plot_density(rawImport, data, ID, summary, dens_dir, night):
    import My_Funcs as my
    plt.ioff()
    # Compute hypnogram
    print("Computing hypno...")
    sls = yasa.SleepStaging(rawImport, eeg_name="EEG")
    hypno = sls.predict()
    print("***HYPNO LENGTH***")
    print(len(hypno))
    # Get number for hypno
    # w=4, rem=3, n1=2, n2=1, n3=0
    hypno_enum = my.hypno_to_plot_art(hypno)

    # Create 60 second epoch hypno_enum
    hypno_enum_60 = [val for val in hypno_enum for _ in (0, 1)]

    bucket_size = 60  # Seconds

    # Create bucket vec with each element 1 second in time
    spindle_count_time = np.zeros(round(data["TimeVec"][-1] + 1))
    print(len(spindle_count_time))

    print("Filling buckets...")
    for index, row in summary.iterrows():
        # Get start time
        start = int(row['Start'])

        # Add one to the corresponding spindle bucket
        spindle_count_time[start] = spindle_count_time[start] + 1

    print("Dividing buckets...")
    # Divide the spindle bucket array into correct bucket sizes
    numberOfBuckets = len(spindle_count_time) / bucket_size
    arrayOfBuckets = np.array_split(spindle_count_time, numberOfBuckets)

    # Append the sum of each bucket to a new vector
    print("Summing buckets...")
    sumBuckets = []
    for i in range(len(arrayOfBuckets)):
        sumBuckets.append(sum(arrayOfBuckets[i]))

    # Create time vec for bar graph
    timeBuckets = range(1, len(sumBuckets) + 1)

    # Plot the sum buckets graph
    plt.clf()
    print("Plotting buckets...")
    Plot, Axis = plt.subplots(2)
    Axis[0].plot(timeBuckets, sumBuckets)
    Axis[0].set_title("Spindle Density and Hypnogram")
    Axis[0].set_ylabel("Occurrences")

    Axis[1].plot(hypno_enum_60)
    Axis[1].set_yticks(ticks=[0, 1, 2, 3, 4])
    lab = ["N3", "N2", "N1", "R", "W"]
    Axis[1].set_yticklabels(lab)
    Axis[1].set_xlabel("Time (60s Buckets)")

    print("saving figure...")
    figure_file = 'Density_Hypno_%s_%s' % (ID, str(night))
    figure_path = dens_dir / figure_file
    plt.savefig(figure_path)


def time_frequency_analysis(data, summary):

    print("Completing time frequency analysis...")

    # Make array for storing indices of spindle detections to remove
    multPeak = np.zeros(len(summary))

    # Var for indexing since index is not consistently increasing by one in summary
    idex = 0
    spindlesRemoved = 0
    for index, row in summary.iterrows():

        # Find start and stop times
        start = int(np.floor(row['Start']) * data['fs'])
        stop = int(np.ceil(row["End"]) * data['fs'])

        # Define frequency range to examine
        freqs = np.linspace(9, 20, num=60)

        # Reshape data into the proper shape for mne function
        inp = np.reshape(data["EEG"][start:stop], (1, 1, len(data["EEG"][start:stop])))

        # Compute time frequency
        power = mne.time_frequency.tfr_array_morlet(inp, data["fs"], output='power', n_cycles=5,
                                                    freqs=freqs)

        # Reshape data for im.show() function
        power = np.reshape(power, (60, stop - start))

        # Remove the half second buffers
        toGraph = power[0:60, 128:stop - start - 128]

        # Take mean power for each frequency value
        ave = np.mean(toGraph, axis=1)

        # Find the peaks frequencies
        peaks, properties = scipy.signal.find_peaks(ave)

        # If we detect multiple peaks
        if len(peaks) != 1:
            # Increment spindles removed counter
            spindlesRemoved = spindlesRemoved + 1

            # Mark the spindle for removal
            multPeak[idex] = 1

        # Iterate index variable
        idex = idex + 1

    # Remove these spindles from summary
    summary["Mult_Peaks"] = multPeak
    summary = summary.loc[summary["Mult_Peaks"] == 0]

    return summary
