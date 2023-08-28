"""
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Sitaram Group 
APNEA Project Summer 2023
Andrea Sanchez Corzo & Zachary Loschinskey

Collection of functions needed to run the APNEA project preprocessing,
spindle detection, postprocessing, and statistics.

This file must be included in the folder running the Blocks of code in the
pipeline for proper functioning.
"""

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import pandas as pd
import yasa
import mne
from scipy.signal import hilbert

# Setup custom plot function
def my_plot(signalVec, timeVec, plotTitle, figureNumber):
  plt.figure(figureNumber)
  plt.plot(timeVec, signalVec)
  plt.title(plotTitle)
  plt.xlabel("Time (s)")
  plt.ylabel("Voltage (uV)")
  plt.show()


def take_envelope(signal):
    # Apply the Hilbert transform to obtain the analytic signal
    analytic_signal = hilbert(signal)

    # Extract the envelope of the waveform
    envelope = np.abs(analytic_signal)
    
    return envelope

def personal_beta_noise(data):
    # Initialize the beta noise vector to zeor
    personalBetaNoise = np.zeros(len(data["EEG"]))
    
    # Create the hilbert transform envelope
    beta_envelope = take_envelope(data["EEG_Beta"])
    
    # Set the threshold as mean + 2 std
    threshold = np.mean(data["EEG_Beta"]) + (3 * np.std(data["EEG_Beta"]))    
    
    for i in range(len(beta_envelope)):
        if beta_envelope[i] > threshold:
            personalBetaNoise[i] = 1
    
    return personalBetaNoise, threshold
    
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
            hypno_enum.append(0)
        elif hypno[i] == 'N1':
            hypno_enum.append(1)
        elif hypno[i] == 'N2':
            hypno_enum.append(2)
        elif hypno[i] == 'N3':
            hypno_enum.append(3)
        elif hypno[i] == 'R':
            hypno_enum.append(4)
        elif hypno[i] == 'U':
            hypno_enum.append(-2)
        elif hypno[i] == 'A':
            hypno_enum.append(-1)
        else:
            hypno_enum.append(0)
    return hypno_enum


def get_ID(file):
    filee = str(file)
    a = filee.split('\\')
    name = a[-1]
    aa = name.split('_')
    namee = aa[2]
    ID = int(namee[-3:-1] + (namee[-1]))
    return ID


def nrem_densities(spindle_table, hypno_array):
    # Given the spindle summary table and the scoring table
    # This function will calculate the NREM2, NREM3, and NREM(2,3) spindle densities
    
    # Sum up all NREM2 and NREM3 epochs from the hypnogram

    NREM2_prev = hypno_array.count(2)
    NREM3_prev = hypno_array.count(3)
    print(NREM2_prev)
    print(NREM3_prev)

    array = spindle_table["Stage"].values


    try:
        # Sum up the number of spindles in NREM2 and NREM3
        NREM2_Spindle_Count = (array==2).sum()
        NREM3_Spindle_Count = (array==3).sum()
    except:
        print("Problem Calculating density")

    # Calculate Densities (Spindles / Second of Stage)
    if NREM2_prev != 0:
        NREM2_Density = (NREM2_Spindle_Count / (NREM2_prev * 30)) * 60  # NREM2_prev is epochs, each containing 30 seconds. * 60 put it per minute
    else:
        NREM2_Density = 0
    
    if NREM3_prev != 0:
        NREM3_Density = (NREM3_Spindle_Count / (NREM3_prev * 30)) * 60
    else:
        NREM3_Density = 0
    
    total_prev = NREM2_prev + NREM3_prev
    if total_prev != 0:
        NREM23_Density = ((NREM2_Spindle_Count + NREM3_Spindle_Count) / (total_prev * 30)) * 60
    else:
        NREM23_Density = 0
    
    return NREM2_Density, NREM3_Density, NREM23_Density



def upsample_hypno_to_data(hypnoEnum, data):
    # Function to make the hypnoEnum have the same size as the 1D data array
    # Needed for input into the detect_spindles function written by mne
    
    # Each stage is for 30 seconds of data, or 30 Seconds * 256 Hz EEG rate points in the data array
    val = 30*256
    hypnoUpsampledRaw = np.repeat(hypnoEnum, val)
    
    # The last stage likely does not have a full 30 seconds of EEG data corresponding to the stage label,
    # as it is unlikely the recording is in an exact multipl of 30 seconds. Thus, we will cut the hypnoUpsampled
    # array to the size of the data.
    if len(hypnoUpsampledRaw) >= len(data["EEG"]):
        hypnoUpsampled = hypnoUpsampledRaw[0:len(data["EEG"])]   # Was EEG_ArtZero
    else:
        while len(hypnoUpsampledRaw) < len(data['EEG']):
            hypnoUpsampledRaw = np.append(hypnoUpsampledRaw, np.zeros(10000))
            print(len(hypnoUpsampledRaw))
        
        hypnoUpsampled = hypnoUpsampledRaw[0:len(data["EEG"])]   
        print("LENGTHS")
        print(len(hypnoUpsampled))
        print(len(data['EEG']))
    # If the hypnogram is shorter than the data somehow, we will fill the end of the hypnogram with wakefuleness until they are the same length.
    # I will have to investigate the cause of this configuration.
    
    return hypnoUpsampled

def detect_slow_waves(data, hypnoEnumUpsampled):

    # Yasa slow wave detection
    SW = yasa.sw_detect(data["EEG"], sf=data["fs"], hypno=hypnoEnumUpsampled, amp_ptp=[65, 300], remove_outliers=False, coupling=True)
    
    summary = SW.summary()
    summary = pd.DataFrame(summary)
    
    """
    Create graph of average sw shape
    """
    # Create storage vector (large enough to store 1 second in each direction around midpoint)
    ave_sw = np.zeros((256*2) + 1)
    
    print("Calculating average vectors...")
    # Loop through every slow wave detection
    for index, row in summary.iterrows():
        
        # Get indices to slice eeg vector
        mid_index_sample = int(row["NegPeak"] * data["fs"])
        start_index_sample = int(mid_index_sample - (1 * data["fs"]))
        end_index_sample = int(mid_index_sample + (1 * data["fs"])) + 1

        # Slice eeg vector
        sw_eeg = data["EEG"][start_index_sample:end_index_sample]
        
        # Normalize for midpoint to be zero
        correction = sw_eeg[int((data["fs"] * 1)) + 1]

        # Correct the vector
        if correction > 0:
            sw_eeg = sw_eeg + correction
        else:
            sw_eeg = sw_eeg - correction
        
        # Add these values to the storage vector
        for i in range(len(ave_sw)):
            ave_sw[i] += sw_eeg[i]
    
    # After looping through, divie the storage array by the number of slow waves to get the average
    ave_sw = ave_sw / len(summary["NegPeak"])
    
    # Return the table and the average array
    return summary, ave_sw


def detect_spindles(data, hypnoEnum, night, samples1):
    """
    3) Yasa spindle detection
    """
    
    thresh = {'rel_pow': 0, 'corr': 0, 'rms': 2.5}
    hypno_array = [2, 3]  # Include only stages NREM2 and NREM 3 in the spindle detection algorithm
    # TRY THE EPOCHED DATA HERE INSTEAD
    
    
    print("Detecting spindles...")
    sp = yasa.spindles_detect(data["EEG_ArtZero"], data["fs"], ch_names=['EEG'],
                              freq_sp=(9, 15), thresh=thresh, hypno=hypnoEnum, include=[2,3], duration=[0.5, 2.5])
    

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
    Beta_Noise_Personal_Array = np.ones(len(summary))
    
    # Create vector to hold the sleep state of each spindle
    spindleStates = []
    hypnoBySecond = np.repeat(hypnoEnum, 30)
    print(len(hypnoBySecond))

    """
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
    """
    
    # # Mark Spindles for removal
    for i in range(len(Beta_Noise)):
        start = int(summary['Start'][i] * data['fs'])
        end = int(summary["End"][i] * data['fs'])
        
        # If there are no beta arts within spindle range
        if sum(data["Beta_Labels"][start:end]) == 0:
            Beta_Noise[i] = 0  # Set the noize vectors properly
                
        # If there is thresh art in the spindle range
        if np.isnan(sum(data["ArtZero"][start:end])):
            Art_Noise[i] = 1  # Set the noize vectors properly


        # if sum(data["Personal_Beta_Labels"][start:end]) == 0:
        #     Beta_Noise_Personal_Array[i] = 0
               
    # Add the noise vectors to the DataFrame
    summary["Beta_Noise"] = Beta_Noise
    summary["Art_Noise"] = Art_Noise
    summary["Beta_Noise_Personal"] = Beta_Noise_Personal_Array
    
    # Create noise tables
    flat_beta_noise = pd.DataFrame(data["Beta_Labels"])
    # pers_beta_noise = pd.DataFrame(data["Personal_Beta_Labels"])
    
    # Filter flat threshold noise spindles
    summaryFlatThresh = summary.loc[summary["Beta_Noise"] == 0]
    summaryFlatThresh = summaryFlatThresh.loc[summaryFlatThresh["Art_Noise"] == 0]

    # Filter personal threshold noise spindles
    summaryPersonalThresh = summary.loc[summary["Beta_Noise_Personal"] == 0]
    summaryPersonalThresh = summaryPersonalThresh.loc[summaryPersonalThresh["Art_Noise"] == 0]
    
    
    # Filter by noise spindles
    # Return just the flat beta threshold filtered summary
    return summaryFlatThresh # , summaryPersonalThresh # , flat_beta_noise, pers_beta_noise


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

