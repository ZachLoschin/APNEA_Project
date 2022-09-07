# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 15:19:57 2022

@author: asanch24
"""

import pathlib
import My_Funcs as my
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne
import numpy as np
from lspopt import spectrogram_lspopt
from matplotlib.colors import Normalize

"""
Zachary Loschinskey & Andrea Sanchez Corzo
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
22 July 2022
"""

"""
Description:
    This script is for importing raw .edf file data, completing preprocessing, computing the hypnogram for each
    night for each patient, and plot the hypnogram, the spectrogram, PSD and spindle density (based on the 
    spindle table given by YASA).

Inputs to this .py file are 1) The .edf file directory
                            2) The corresponding sleep division Excel file
                            3) The directory to store the figures
                            5) The directory to save error messages

The input directories and folders should be of form:
    1) The .edf file directory:
        -Simply a folder containing all .edf files sequentially by ID
        -The name of the edf file should be of form 0000_0000_000115_Export.edf
        -Nore the number of zeros is not important, simply the placement of the ID ie. 115
    2) The corresponding division Excel division file:
        -This excel file should include fields:
            "SJID", "EDF_File", "EDF_ID", "Night", "RecordingTime", "Case/Control", "OSA/NonOSA"
        - The Recording time is of type float
        - The labels are all of type string "Case", "Control", "OSA", and "nonOSA".
        - Night is of type int, 1 or 2.
"""

"""
MethodsFigure Layout: Import, compute hypnograms, save .pngs
    0) Create directories
    1) Import data
    2) Use recording times to find where to split data
    3) Split the data by night
    4) Compute hypnograms for each night
    5) Compute spectrogram for each night
    6) Compute PSD for each night
    7) Calculate spindle density over time based on the output table from YASA
    5) Plot hypnogram, spectrogram, PSD and spindle density per recording
"""

"""
0) Create Directories
"""
print("Creating directories...")

# Data directory for official runs
data_dir = pathlib.Path("/data/analysis_edfs/")

# Directory for official running
pipdir = pathlib.Path("./MethodsFigs/")
pipdir.mkdir(parents=True, exist_ok=True)

# Shared directory for official runs
#dict_dir = pathlib.Path("./MethodsFigs/Excel_Data_All/")
#dict_dir.mkdir(parents=True, exist_ok=True)

# Plot directory for official runs
dens_dir = pathlib.Path("./MethodsFigs/Figures/")
dens_dir.mkdir(parents=True, exist_ok=True)

# Official error directory
error_dir = pathlib.Path("./MethodsFigs/Error_Storage/")
error_dir.mkdir(parents=True, exist_ok=True)

# Local data for reading in night division data
div_data = pathlib.Path("../Official_Runs_Folder/CompleteTable2.xlsx")

# Read in division data to DataFrame
DivDF = pd.read_excel(div_data, engine='openpyxl')

ID_List = DivDF["EDF_ID"]

files = pathlib.Path(data_dir).glob('*.edf')

# For each .edf file
for file in files:

    # Setup try for each file to not stop running if one error occurs
    try:
        with open(file, 'rb') as f:

            """
            1) Read in EDF
            """
            split_array = str(file).split('\\')
            name = split_array[-1]
            print("Importing data...")
            name = name.split('.')[0]
            print(name)
            filee = str(file)
            a = filee.split('/')
            name = a[-1]
            print(name)
            aa = name.split('_')
            namee = aa[2]
            print(namee)
            ID = int(namee[-3:-1] + (namee[-1]))
            print(ID)

            rawImport = mne.io.read_raw_edf(file, preload=True)

            eeg = rawImport["EEG"][0][0]
            filteredData = rawImport.filter(l_freq=None, h_freq=18, picks=["EEG"], method='iir')

            """
            2) Use recording times to find where to split data
            """
            # Get the recording times for night 1 and 2
            DivDF_Patient = DivDF.loc[DivDF["EDF_ID"] == ID]

            # Find how many nights there is data for
            if len(DivDF_Patient) == 0:
                nights = 0
            elif len(DivDF_Patient) == 1:
                nights = 1
            elif len(DivDF_Patient) == 2:
                nights = 2
            else:
                # Save -1 if there is an unexpected number of nights
                nights = -1

            if nights == 0:
                print("no nights")
                continue
            elif nights == -1:
                continue
            elif nights == 1:
                """
                4) Compute hypnograms for the one night
                """
                Night1_sls = yasa.SleepStaging(raw=rawImport, eeg_name="EEG", eog_name="LEOG")

                # Get hypno objects
                Night1_Hypno = Night1_sls.predict()

                # Convert the hypnograms to numbers
                Night1_HypnoEnum = my.hypno_to_plot_art(Night1_Hypno)

            elif nights == 2:
                Time_N1 = DivDF_Patient.iloc[0]["RecordingTime"]  # in hours
                Time_N2 = DivDF_Patient.iloc[1]["RecordingTime"]  # in hours

                # Convert these recording times to seconds then to samples
                sample_n1 = (Time_N1 * 3600) * rawImport.info["sfreq"]
                sample_n2 = (Time_N2 * 3600) * rawImport.info["sfreq"]

                # If there is left over in the middle, take midpoint
                if sample_n2 + sample_n1 < len(eeg):
                    print("Sum less than EEG")
                    gap = len(eeg) - sample_n2 - sample_n1  # Changed from a plus to a minus sign

                    # Set sample one to include first half of gap
                    sample_n1 = sample_n1 + (0.5 * gap)

                    # Set sample 2 to include samples from middle of gap to end
                    sample_n2 = len(eeg) - sample_n1

                elif sample_n2 + sample_n1 > len(eeg):
                    print("Sum greater than EEG")
                    
                    # Calculate overlap
                    overlap = abs(len(eeg) - sample_n1 - sample_n2)

                    # Set sample one to exclude half of gap
                    sample_n1 = sample_n1 - (0.5 * overlap)

                    # Set sample 2 to include samples from middle of overlap to end
                    sample_n2 = len(eeg) - sample_n1

                """
                3) Split up by night
                """
                # Copy raw import to second one for cropping night 2
                rawImport2 = rawImport.copy()
                # Split the data into two nights
                Night_1 = rawImport.crop(tmin=0, tmax=sample_n1 / rawImport.info["sfreq"], include_tmax=False)
                Night_2 = rawImport2.crop(tmin=sample_n1 / rawImport.info["sfreq"],
                                          tmax=(len(rawImport2) / rawImport.info["sfreq"]) - 60, include_tmax=False)
    except:
        print("PROBLEM PROBLEM PROBLEM ***** : ID = %s" % ID)
        error_file = '%s_%s.txt' % (ID, 'ErrorMSG')
        error_path = error_dir / error_file
        with open(error_path, 'w') as e:
            e.write('Error running %s\n' % ID)

