import pathlib
import My_Funcs as my
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import numpy as np
import mne
from matplotlib.widgets import Slider

"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
19 July 2022
"""

"""
Description: Slow wave detection code.
    0) Create directories
    1) Import data
    2) Creation of our data dictionary
    3) Split data by night
    4) YASA slow wave detection
    5) Save output

"""


# Slow Wave detection funciton
def detect_slow_wave(Data):
    sw = yasa.sw_detect(Data, sf=256)
    return sw.summary()


# Path for input EDF Files
edf_path = pathlib.Path("C:\\Users\\Zachary Loschinskey\\OneDrive\\Desktop\\APNEA_Tests\\Test_EDFs")
files = pathlib.Path(edf_path).glob('*')

# Path for output storage
output_path = pathlib.Path("C:\\Users\\Zachary Loschinskey\\OneDrive\\Desktop\\APNEA_Tests\\Output")

# Path for error storage
error_path = pathlib.Path("C:\\Users\\Zachary Loschinskey\\OneDrive\\Desktop\\APNEA_Tests\\Error_Storage")

# Import the data
for file in files:
    # count = count + 1
    # Setup try for each file to not stop running if one error occurs
    # try:
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

        eeg = rawImport["EEG"][0][0]

        """
        2) Creation of our data dictionary
        """
        print("Creating dict...")
        # Create epoch vector
        epochVec = my.create_epochs(rawImport["EEG"][0][0], rawImport.info["sfreq"], 30)

        # Create epoch time vector
        epochTimeVec = my.create_epochs(rawImport["EEG"][1], rawImport.info["sfreq"], 30)

        # Create Dictionary for organization
        data = my.create_dict(rawImport["EEG"][0][0], rawImport.info["sfreq"], rawImport["EEG"][1], epochVec,
                              epochTimeVec)

        # Set artifacts to zero
        data["ArtZero"] = data["EEG"]
        for i in range(len(data["ArtZero"])):
            if abs(data["EEG"][i]) >= 250:
                data["ArtZero"][i] = 0


        """
        3) Split data by night -- Empty for now
        """

        """
        4) Yasa slow wave detection
        """
        print("Detecting slow waves...")
        swDF = detect_slow_wave(data["EEG"])


        """
        CREATE SLOW WAVE VECTOR FOR GRAPHING
        """
        # mark zeros where no slow wave is detected and 50 where they are
        data["sw_vec"] = np.zeros(len(data["EEG"]))
        count = 0
        # Go through summary file of sw and set spindle vec values
        for index, row in swDF.iterrows():
            start = int(row['Start'] * data['fs'])
            end = int(row["End"] * data['fs'])

            data["sw_vec"][start:end] = 50
            data["sw_vec"][start - 1] = 0
            data["sw_vec"][end + 1] = 0

            count = count + 1
            print("Spindles set: %d" % count)

        """
        5) Save to excel
        """
        print("Saving to excel...")
        swFile = "SlowWaves_%s_N1.xlsx" % ID
        swPath = output_path / swFile
        swDF.to_excel(swPath)

        # start = 10000
        # finish = 20000
        #
        # plt.plot(data["TimeVec"][start:finish], data["ArtZero"][start:finish])
        # plt.plot(data["TimeVec"][start:finish], data["sw_vec"][start:finish], color='r')

        """
        6) Create slider plot
        """
        print("Creating slider plot...")
        plt.clf()
        Plot, Axis = plt.subplots(2, sharex=True)

        plt.subplots_adjust(bottom=0.25)

        # Data plots
        Axis[0].plot(data["TimeVec"], data["ArtZero"])

        # Spindle detection plots
        Axis[0].plot(data["TimeVec"], data["sw_vec"], color='r')

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

            Plot.canvas.draw_idle()
            # plt.ylim([-30, 30])  # is this needed?
            # Axis[0].set_ylim([-300, 300])
            # Axis[1].set_ylim([-300, 300])
            Axis[0].set_ylim([-250, 250])

            # Axis[0].set_title('EEG, Artifacts = 0')
            #
            # for index in range(0, 1):
            #     Axis[index].spines['right'].set_visible(False)
            #     Axis[index].spines['top'].set_visible(False)
            #     Axis[index].spines['bottom'].set_visible(False)
            #     Axis[index].xaxis.set_visible(False)

        # update function called using on_changed() function
        slider_position.on_changed(update)

        # Display the plot
        # plt.ylim([-40, 40])
        # Axis[0].set_ylim([-300, 300])
        # Axis[1].set_ylim([-300, 300])
        Axis[0].set_ylim([-250, 250])

        Axis[0].set_title('EEG, Artifacts = 0')

        plt.show()

    # except:
    #     print("PROBLEM PROBLEM PROBLEM ***** : ID = %s" % ID)
    #     error_file = '%s_%s.txt' % (ID, 'ErrorMSG')
    #     error_path = error_path / error_file
    #     with open(error_path, 'w') as e:
    #         e.write('Error running %s\n' % ID)
