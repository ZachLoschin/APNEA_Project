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
    2) Creation of our data dictionary
    3) Artifact removal label vector creation
    4) Band pass filter the EEG_ArtZero data (9-15Hz)
    5) Upper Beta pass filter to graph (20-30 Hz)
    6) Remove artifacts using label vector
    7) Split the data by the night vector
    
    8) Yasa spindle detection
    9) Learn the spindle object
    10) Spectrogram analysis

"""

"""
0) Create Directories
"""

print("Creating directories...")

"""
# Data directory for official runs
data_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/APNEA Raw Files/AllEDFs/")

# Directory for official running
block3dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3_51/")
block3dir.mkdir(parents=True, exist_ok=True)

# Shared directory for official runs
dict_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3_51/Excel_Data_All/")
dict_dir.mkdir(parents=True, exist_ok=True)

# Plot directory for official runs
dens_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3_51/Density_Hypno_Plots/")

# Official error directory
error_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block3_51/Error_Storage/")
error_dir.mkdir()
"""

# Local data folder for testing
block3dir = pathlib.Path("Block3_Local/Data")
block3dir.mkdir()

# Local dict for testing
dict_dir = pathlib.Path("Block3_Local/Excel_Data/")

# Local data directory for testing
data_dir = pathlib.Path("Block3_Local/Data")
files = pathlib.Path(data_dir).glob('*')

# Local plot saving directory for testing
dens_dir = pathlib.Path("Block3_Local/Plot_Data")
dens_dir.mkdir(parents=True, exist_ok=True)

"""
Create dataframe to hold spindle percentage data
"""
SpindlePerc = pd.DataFrame(columns=["ID", "Night_Number", "W_Spindles", "REM_Spindles", "N3_Spindles",
                                    "N2_Spindles", "N1_Spindles", "W_Time", "REM_Time", "N3_Time",
                                    "N2_Time", "N1_Time"])

# Set up try except block
try:
    # Import the data
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

            # Add EOG channels to the dictionary
            data["REOG"] = rawImport["REOG"][0][0]
            data["LEOG"] = rawImport["LEOG"][0][0]
            data["HMov"] = rawImport["HMov"][0][0]

            """
            3) Artifact removal (create label vec with artifact locations as Nan)
            """
            start = 100000
            finish = start + 7680

            print("Creating artifact label vector...")
            data["ArtZero"] = np.zeros(len(data["EEG"]))
            for i in range(len(data["ArtZero"])):
                if abs(data["EEG"][i]) >= 250:
                    data["ArtZero"][i] = np.nan

            # EOG Channels artifact removal
            for i in range(len(data["LEOG"])):
                if abs(data["LEOG"][i]) >= 250:
                    data["LEOG"][i] = 0

            for i in range(len(data["REOG"])):
                if abs(data["REOG"][i]) >= 250:
                    data["REOG"][i] = 0

            """
            4) Band pass filter the EEG data (10-16 Hz)
            """
            print("Bandpass filtering...")
            data["EEG_Filt"] = my.butter_bandpass_filter(data["EEG"], 10, 16, data["fs"], order=5)

            """
            5) Upper Beta pass filter to graph (20-50 Hz)
            """
            print("Beta pass filtering...")
            data["EEG_Beta"] = my.butter_bandpass_filter(data["EEG"], 20, 50, data["fs"], order=5)
            data["Beta_Labels"] = np.zeros(len(data["EEG_Beta"]))

            # For any threshold event, change the beta label vec to 1
            for i in range(len(data["EEG_Beta"])):
                if data["EEG_Beta"][i] > 10:
                    data["Beta_Labels"][i - 64:i + 64] = 1

            """
            6) Remove artifacts using the label vector
            """
            print("Removing artifacts...")
            data["EEG_ArtZero"] = data["EEG"]
            for i in range(len(data["EEG"])):
                if np.isnan(data["ArtZero"][i]):
                    data["EEG_ArtZero"][i] = 0
                    data["EEG_Filt"][i] = 0
                    data["EEG_Beta"][i] = 0

            """
            7) Split the data by the night vector
            """


except:
    print("Bruh moment...")
































