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
import os; os.system("clear")
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
data_dir = pathlib.Path("./data/")
data_dir.mkdir(parents=True, exist_ok=True)

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
div_data = pathlib.Path("./data/CompleteTable2.xlsx")

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
            #filteredData = rawImport.filter(l_freq=None, h_freq=18, picks=["EEG"], method='iir')

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
                # Get total time of recording
                total_time = DivDF_Patient.iloc[0]['RecordingTime'] # in hours

                # Get sampling frequency
                samp_freq = rawImport.info['sfreq']

                # Convert these recording times to seconds then to samples
                total_samples = (total_time * 3600) * samp_freq

                # Get data from Airflow
                data, time = rawImport['Airflow']
                data = np.squeeze(data) # reduces data dimensions

                # Find peaks in Airflow data
                peaks_values = [] # peaks_freq list
                for peak_freq in data:
                    if peak_freq > 3000:
                        peaks_values.append(peak_freq)
                
                #print(peaks_freq)
                
                peaks_keys = [] # peak_index list
                peaks_bool = data > 3000 # could be any number over 2000 probably
                for peak_index, peak in enumerate(peaks_bool):
                    if peak_index:
                        # If the peak is over 3000:
                        if peak:
                            peaks_keys.append(peak_index)
                
                # Creats dict
                peaks = {}
                for key in peaks_keys:
                    for value in peaks_values:
                        peaks[key] = value
                        peaks_values.remove(value)  
                        break

                #print(peaks)

                # Assumes peak is at least 1 hr from start and 1 hr from finish
                for key in peaks.copy():
                    if key <= samp_freq * 3600: #or key >= total_samples - samp_freq * 3600:
                        peaks.pop(key)

                print(peaks)

                # Finds max peak
                max_peak = max(peaks)

                print(max(data))

                # # Divide nights
                # night_1 = rawImport.copy().crop(tmin=0, tmax=max_peak/256)
                # night_2 = rawImport.copy().crop(tmin=max_peak/256)

                # # Assign and plot divided nights
                # data, time = night_1['Airflow']
                # data = np.squeeze(data)
                # plt.plot(time, data)
                # plt.show()

                # data, time = night_2['Airflow']
                # data = np.squeeze(data)
                # plt.plot(time, data)
                # plt.show()

    except Exception as e:
        print(str(e))
        print("PROBLEM PROBLEM PROBLEM ***** : ID = %s" % ID)
        error_file = '%s_%s.txt' % (ID, 'ErrorMSG')
        error_path = error_dir / error_file
        with open(error_path, 'w') as file:
            file.write(str(e))
