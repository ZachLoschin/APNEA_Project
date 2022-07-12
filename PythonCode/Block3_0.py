import pathlib
import My_Funcs as my
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne
import scipy.signal
from matplotlib.widgets import Slider

"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
14 June 2022, 15 June 2022, 17 June 2022, 21 June 2022
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
        -Includes saving excel
    4.5) Plot and average template
    5) Plotting spindles over time bar graph
    6) Plotting spindle spectrograms
    7) Plotting with slider
"""

"""
0) Create directories
"""
print("Creating directories...")
block3dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3/")
# block3dir.mkdir(parents=True, exist_ok=True)

# dict_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3/Excel_Data_All/")
dict_dir = pathlib.Path("../Block3_Local/Excel_Data/")
# dict_dir.mkdir(parents=True, exist_ok=True)

# Data dir for smoothed data
# data_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/APNEA Raw Files/AllEDFs/")
data_dir = pathlib.Path("../Block3_Local/Data/")
files = pathlib.Path(data_dir).glob('*')

# dens_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3/Density_Hypno_Plots_All/")
dens_dir = pathlib.Path("../Block3_Local/Plot_Data/")
# dens_dir.mkdir(parents=True, exist_ok=True)

"""
Create dataframe to hold spindle percetage data
"""
SpindlePerc = pd.DataFrame(columns=["ID", "W", "REM", "N3", "N2", "N1"])

# Import data
for file in files:
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

        # Define path
        dict_file = 'SpindleData_%s.xlsx' % ID
        dict_path = dict_dir / dict_file

        # Save this data to excel
        print("Saving to excel...")
        summary.to_excel(dict_path, index=False)

        """
        4.5) Plot and average template NOT FUNCTIONAL RIGHT NOW (6/21/2022)
        """
        # print("Plotting average template...")
        # plt.clf()
        # sp.plot_average()
        # plt.show()

        """
        5) Plotting spindle density and hypnogram 
        """
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
        4.25) Calculate and save percent of spindles that are in each stage
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

        # Check if the sum30 and hypno_enum lengths are the same -- they should be
        # Only proceed if this is the case
        print("Printing lengths sum30, hypno_enum...")
        print(len(sum30))
        print(len(hypno_enum))
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
                    n2Spindles / spindleTotal, n1Spindles / spindleTotal]
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

        """
        6) Plotting spindle spectrograms NOT FUNCTIONAL AS OF 2/21/2022
        """
        # # Plot the spectrogram from these points +- 1 second * (256 Hz)
        # for index, row in summary.iterrows():
        #     # Get start and end times for a spindle
        #     start = int(row['Start'])
        #     end = int(row['End'])
        #
        #     print("Plotting Spectrogram...")
        #     plt.clf()
        #     yasa.plot_spectrogram(data["EEG_ArtZero"][start - 512:end + 512], data["fs"], win_sec=0.25)
        #     plt.show()

        """
        7) PLOTTING WITH SLIDER 
        """

        """
        USE THIS FOR VISUALIZATION, DO NOT RUN ON ALL PATENT'S DATA
        """
        print("Creating slider plot...")
        plt.clf()
        Plot, Axis = plt.subplots(6, sharex=True)

        plt.subplots_adjust(bottom=0.25)

        # Data plots
        Axis[0].plot(data["TimeVec"], data["EEG_ArtZero"])
        Axis[1].plot(data["TimeVec"], data["LEOG"])
        Axis[2].plot(data["TimeVec"], data["REOG"])
        Axis[3].plot(data["TimeVec"], data["HMov"])
        Axis[4].plot(data["TimeVec"], data["EEG_Beta"])
        Axis[5].plot(data["TimeVec"], data["EEG_Filt"])

        # Spindle detection plots
        Axis[0].plot(data["TimeVec"], data["Spindle_Vec"], color='r')
        Axis[1].plot(data["TimeVec"], data["Spindle_Vec"], color='r')
        Axis[2].plot(data["TimeVec"], data["Spindle_Vec"], color='r')
        Axis[3].plot(data["TimeVec"], data["Spindle_Vec"], color='r')
        Axis[4].plot(data["TimeVec"], data["Spindle_Vec"], color='r')
        Axis[5].plot(data["TimeVec"], data["Spindle_Vec"], color='r')

        # Choose the Slider color
        slider_color = 'White'

        # Set the axis and slider position in the plot
        axis_position = plt.axes([0.2, 0.1, 0.65, 0.03],
                                 facecolor=slider_color)
        slider_position = Slider(axis_position,
                                 'Pos', 0.1, 100000)

        # update() function to change the graph when the slider is in use
        def update(val):
            pos = slider_position.val
            Axis[0].axis([pos, pos + 20, -1, 1])
            Axis[1].axis([pos, pos + 20, -1, 1])
            Axis[2].axis([pos, pos + 20, -1, 1])
            Axis[3].axis([pos, pos + 20, -1, 1])
            Axis[4].axis([pos, pos + 20, -1, 1])
            Axis[5].axis([pos, pos + 20, -1, 1])

            Plot.canvas.draw_idle()
            # plt.ylim([-30, 30])  # is this needed?
            # Axis[0].set_ylim([-300, 300])
            # Axis[1].set_ylim([-300, 300])
            Axis[0].set_ylim([-50, 50])
            Axis[1].set_ylim([-50, 50])
            Axis[2].set_ylim([-300, 300])
            Axis[3].set_ylim([0, 6])
            Axis[4].set_ylim([-35, 35])
            Axis[5].set_ylim([-35, 35])

            Axis[0].set_title('EEG, Artifacts = 0')
            Axis[1].set_title('LEOG, Artifacts = 0')
            Axis[2].set_title('REOG, Artifacts = 0')
            Axis[3].set_title('HMov')
            Axis[4].set_title('Upper Beta (20-50 Hz)')
            Axis[5].set_title('Bandpass Filtered (10-16Hz)')

            for index in range(0, 5):
                Axis[index].spines['right'].set_visible(False)
                Axis[index].spines['top'].set_visible(False)
                Axis[index].spines['bottom'].set_visible(False)
                Axis[index].xaxis.set_visible(False)

            Axis[5].spines['right'].set_visible(False)
            Axis[5].spines['top'].set_visible(False)

        # update function called using on_changed() function
        slider_position.on_changed(update)

        # Display the plot
        plt.ylim([-40, 40])
        # Axis[0].set_ylim([-300, 300])
        # Axis[1].set_ylim([-300, 300])
        Axis[0].set_ylim([-50, 50])
        Axis[1].set_ylim([-50, 50])
        Axis[2].set_ylim([-300, 300])
        Axis[3].set_ylim([0, 6])
        Axis[4].set_ylim([-40, 40])
        Axis[5].set_ylim([-40, 40])

        Axis[0].set_title('EEG, Artifacts = 0')
        Axis[1].set_title('LEOG, Artifacts = 0')
        Axis[2].set_title('REOG, Artifacts = 0')
        Axis[3].set_title('HMov')
        Axis[4].set_title('Upper Beta (20-50 Hz)')
        Axis[5].set_title('Bandpass Filtered (10-16Hz)')
        plt.show()

"""
After patient loop
"""
