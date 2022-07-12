import pathlib
import My_Funcs as my
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne
import scipy.signal

"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
23 June 2022
"""

"""
Block Layout:
    0) Create directories
    1) Import data
    1.25) Creation of our data dictionary
    1.5) Artifact removal label vector creation
    2) Band pass filter the EEG_ArtZero data (9-15Hz)
    2.5) Upper Beta pass filter to graph (20-30 Hz)
    3) Yasa spindle detection
    3.5) Remove artifacts using the label vector
    4) Learn the spindle object
    4.25) Spectrogram analysis
    
"""

"""
0) Create directories
"""
print("Creating directories...")

# Directory for official running
block3dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3_52/")
block3dir.mkdir(parents=True, exist_ok=True)

# Local directory for testing
# block3dir = pathlib.Path("Block3_Local/Data")
# block3dir.mkdir()

# Shared directory for official run
dict_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3_52/Excel_Data_All/")

# Local directory for testing
#dict_dir = pathlib.Path("Block3_Local/Excel_Data/")
dict_dir.mkdir(parents=True, exist_ok=True)

# Data directory for official runs
data_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/APNEA Raw Files/AllEDFs/")

# Local directory for testing
# ata_dir = pathlib.Path("Block3_Local/Data")
files = pathlib.Path(data_dir).glob('*')

# Plot directory for official runs
dens_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3_52/Density_Hypno_Plots/")

# Local directory for testing
# dens_dir = pathlib.Path("Block3_Local/Plot_Data")
dens_dir.mkdir(parents=True, exist_ok=True)

error_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3_52/Error_Storage/")
error_dir.mkdir(parents=True, exist_ok=True)

"""
Create dataframe to hold spindle percentage data
"""
SpindlePerc = pd.DataFrame(columns=["ID", "W_Spindles", "REM_Spindles", "N3_Spindles", "N2_Spindles", "N1_Spindles",
                                    "W_Time", "REM_Time", "N3_Time", "N2_Time", "N1_Time"])

# Import data
for file in files:
    try:
        with open(file, 'rb') as f:
            """
            1) Raw data import
            """
            split_array = str(file).split('\\')
            name = split_array[-1]
            print("Importing data...")
            rawImport = mne.io.read_raw_edf(file, preload=True)

            name = name.split('.')[0]
            print(name)
            ID = my.get_ID(file)
            print(ID)

            """
            1.25) Creation of our data dictionary
            """
            # print("Resampling to 100Hz")
            # rawImport.resample(100)

            print("Creating dict...")
            # Create epoch vector
            epochVec = my.create_epochs(rawImport["EEG"][0][0], rawImport.info["sfreq"], 30)

            # Create epoch time vector
            epochTimeVec = my.create_epochs(rawImport["EEG"][1], rawImport.info["sfreq"], 30)

            # Create Dictionary for organization
            data = my.create_dict(rawImport["EEG"][0][0], rawImport.info["sfreq"], rawImport["EEG"][1], epochVec,
                                  epochTimeVec)

            print(data["TimeVec"])
            # Add EOG channels to the dictionary
            data["REOG"] = rawImport["REOG"][0][0]
            data["LEOG"] = rawImport["LEOG"][0][0]
            data["HMov"] = rawImport["HMov"][0][0]

            """
            1.5) Artifact removal (create label vec with artifact locations as Nan)
            """
            start = 100000
            finish = start+7680

            print("Creating artifact label vector...")
            data["ArtZero"] = np.zeros(len(data["EEG"]))
            for i in range(len(data["ArtZero"])):
                if abs(data["EEG"][i]) >= 250:
                    data["ArtZero"][i] = np.nan

            # EOG Channels arifact removal
            for i in range(len(data["LEOG"])):
                if abs(data["LEOG"][i]) >= 250:
                    data["LEOG"][i] = 0

            for i in range(len(data["REOG"])):
                if abs(data["REOG"][i]) >= 250:
                    data["REOG"][i] = 0

            """
            2) Band pass filter the EEG data (10-16 Hz)
            """
            print("Bandpass filtering...")
            data["EEG_Filt"] = my.butter_bandpass_filter(data["EEG"], 10, 16, data["fs"], order=5)

            """
            2.5) Upper Beta pass filter to graph (20-50 Hz)
            """
            print("Beta pass filtering...")
            data["EEG_Beta"] = my.butter_bandpass_filter(data["EEG"], 20, 50, data["fs"], order=5)
            data["Beta_Labels"] = np.zeros(len(data["EEG_Beta"]))

            # For any threshold event, change the beta label vec to 1
            for i in range(len(data["EEG_Beta"])):
                if data["EEG_Beta"][i] > 10:
                    data["Beta_Labels"][i-64:i+64] = 1
            print("BETA LABELS")
            print(sum(data["Beta_Labels"]))

            """
            3.5) Remove artifacts using the label vector
            """
            print("Removing artifacts...")
            data["EEG_ArtZero"] = data["EEG"]
            for i in range(len(data["EEG"])):
                if np.isnan(data["ArtZero"][i]):
                    data["EEG_ArtZero"][i] = 0
                    data["EEG_Filt"][i] = 0
                    data["EEG_Beta"][i] = 0

            """
            3) Yasa spindle detection
            """
            print("Detecting spindles...")
            thresh = {'rel_pow': None, 'corr': None, 'rms': 2}
            # TRY THE EPOCHED DATA HERE INSTEAD
            sp = yasa.spindles_detect(data["EEG_ArtZero"], data["fs"], ch_names=['EEG'], freq_sp=(9, 15), thresh=thresh)

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

            for index, row in summary.iterrows():

                start = int(row['Start'] * data['fs'])
                end = int(row["End"] * data['fs'])

                # If there are no beta or threshold artifacts within the spindle range
                if sum(data["Beta_Labels"][start:end]) == 0:  # and np.isnan(sum(data["ArtZero"][start:end])) is False:
                    data["Spindle_Vec"][start:end] = 20
                    data["Spindle_Vec"][start - 1] = 0
                    data["Spindle_Vec"][end + 1] = 0

                count = count+1
                print("Spindles set: %d" % count)

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

            """
            4.25) Spectrogram analysis
            """
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
                power = np.reshape(power, (60, stop-start))

                # Remove the half second buffers
                toGraph = power[0:60, 128:stop-start-128]

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
                idex = idex+1

            # Remove these spindles from summary
            summary["Mult_Peaks"] = multPeak
            summary = summary.loc[summary["Mult_Peaks"] == 0]

            """
            Plotting settings below, keeping here for reference.
            """
            # plt.clf()
            # plt.figure(1, figsize=(80, 80), dpi=100)
            # plt.imshow(toGraph, cmap='rainbow', interpolation='bilinear', aspect='auto')
            # ticks = np.linspace(9, 20, num=40)
            # plt.ylim(9, 20)
            # plt.yticks(ticks)
            # plt.show()
            #
            # plt.clf()
            # plt.plot(ave)
            # plt.show()

            """
            4.75) Add Sleep stage to each detected spindle
            """
            # Compute hypnogram and convert to numbers
            print("Computing hypno...")
            sls = yasa.SleepStaging(rawImport, eeg_name="EEG")
            hypno = sls.predict()
            print("***HYPNO LENGTH***")
            print(len(hypno))
            # Get number for hypno
            # w=4, rem=3, n1=2, n2=1, n3=0
            hypno_enum = my.hypno_to_plot_art(hypno)

            # Add a buffer to hypno enum, so it is large enough for looping
            hypno_enum_buffer = hypno_enum
            hypno_enum_buffer.append(hypno_enum[-1])

            # Calculate percent time spent in each sleep stage
            w, r, n1, n2, n3 = 0, 0, 0, 0, 0

            # Mark how many of each stage there are in hypno_enum
            for element in hypno_enum:
                if element == 4:
                    w = w+1
                elif element == 3:
                    r = r+1
                elif element == 2:
                    n1 = n1+1
                elif element == 1:
                    n2 = n2+1
                elif element == 0:
                    n3 = n3+1

            # Add percent of time in each sleep stage to the DataFrame
            summary['Wake_Frac'] = (w/len(hypno_enum))
            summary['REM_Frac'] = (r/len(hypno_enum))
            summary['N1_Frac'] = (n1/len(hypno_enum))
            summary['N2_Frac'] = (n2/len(hypno_enum))
            summary['N3_Frac'] = (n3/len(hypno_enum))

            # Create index for iterating
            iterr = 0

            # Create vector for state storage, initialize to number 5
            # Use this initialization, so we can see if there is any problem
            # As no sleep state will have the label 5
            states = np.zeros(len(summary)) + 5

            # Loop through all spindles
            for index, row in summary.iterrows():

                # Find start time of the spindle in seconds
                start = row['Start']

                # Find which to which 30 second epoch the spindle belongs
                epoNumber = round(start / 30)

                # Add the state to the state vector
                states[iterr] = hypno_enum_buffer[epoNumber]
                # Increment iteration var
                iterr = iterr + 1

            # Add the states vector to the dataframe
            summary["State"] = states

            # Define path for saving xlsx
            dict_file = 'SpindleData_%s.xlsx' % ID
            dict_path = dict_dir / dict_file

            # Save spindle data to excel
            print("Saving to excel...")
            summary.to_excel(dict_path, index=False)

            """
            5) Plotting spindle density and hypnogram
            """
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
            timeBuckets = range(1, len(sumBuckets)+1)

            # Plot the sum buckets graph
            plt.clf()
            print("Plotting buckets...")
            Plot, Axis = plt.subplots(2)
            Axis[0].plot(timeBuckets, sumBuckets)
            Axis[0].set_title("Spindle Occurrences per Bucket of Time: %ds" % bucket_size)
            Axis[0].set_ylabel("Occurrences")

            Axis[1].plot(hypno_enum_60)
            Axis[1].set_yticks(ticks=[0, 1, 2, 3, 4])
            lab = ["N3", "N2", "N1", "R", "W"]
            Axis[1].set_yticklabels(lab)

            figure_file = 'Density_Hypno_%s' % ID
            figure_path = dens_dir / figure_file
            plt.savefig(figure_path)

            """
            5.25) Calculate and save percent of spindles that are in each stage
            """
            # Divide the spindle array into 30 second buckets
            numberOfBuckets = len(spindle_count_time) / 30
            arrayOfBuckets = np.array_split(spindle_count_time, numberOfBuckets)

            # Append the 30-second totals to a new vector
            sum30 = []
            for i in range(len(arrayOfBuckets)):
                sum30.append(sum(arrayOfBuckets[i]))

            # Keep total number of spindles
            spindleTotal = sum(sum30)
            wSpindles = 0
            rSpindles = 0
            n1Spindles = 0
            n2Spindles = 0
            n3Spindles = 0

            """
            There is an issue with sum30 and hypno_enum having a difference in one in their size.
            This is probably caused by differences in rounding during creation of sum30 and in
            computation of the hypnogram by yasa. We will simply cut out the last element of the
            larger array to continue with our process wit minimal error.
            """
            if len(sum30) > len(hypno_enum):
                print("Truncating sum30...")
                sum30 = sum30[:len(hypno_enum)]
            elif len(hypno_enum) > len(sum30):
                print("Truncating hpyno_enum...")
                hypno_enum = hypno_enum[:len(sum30)]

            # Still be cautious and only continue if they are indeed the same length
            if len(sum30) == len(hypno_enum):
                print("***SUM AND HYPNOENUM EQUAL LENGTH***")

                # Check each 30-second bucket for the sleep state and count number of spindles per state
                for i in range(len(sum30)):
                    if hypno_enum[i] == 4:
                        wSpindles = wSpindles + sum30[i]
                    elif hypno_enum[i] == 3:
                        rSpindles = rSpindles + sum30[i]
                    elif hypno_enum[i] == 2:
                        n1Spindles = n1Spindles + sum30[i]
                    elif hypno_enum[i] == 1:
                        n2Spindles = n2Spindles + sum30[i]
                    else:
                        n3Spindles = n3Spindles + sum30[i]

                # Create array to be put into df
                toDF = [ID, wSpindles / spindleTotal, rSpindles / spindleTotal, n3Spindles / spindleTotal,
                        n2Spindles / spindleTotal, n1Spindles / spindleTotal, w/len(hypno_enum), r/len(hypno_enum),
                        n3/len(hypno_enum), n2/len(hypno_enum), n1/len(hypno_enum)]
            else:
                print("***SUM AND HYPNOENUM NOT EQUAL LENGTH***")
                toDF = [ID, 'Error', 'Error', 'Error', 'Error', 'Error']

            # Save array to df
            SpindlePerc.loc[len(SpindlePerc.index)] = toDF

            """
            Overwrite the dictionary everytime to avoid loss of data if later error
            """
            # Define path
            perc_file = 'Percentage_Data_Subset2.xlsx'
            perc_path = dict_dir / perc_file

            print("Saving perc data...")
            # Save Spindle Perc to an Excel file
            SpindlePerc.to_excel(perc_path)
    except:
        print("ERROR RUNNING %s" % ID)
        error_file = 'Error_%s' % ID
        error_path = error_dir / error_file
        with open(error_path, 'w') as e:
            e.write('Error running %s\n' % ID)
