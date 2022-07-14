import pathlib
import My_Funcs as my
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne
import edflib
import scipy.signal

"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
12 July 2022
"""

"""
1) Read in .EDF file
2) Get total recording time
3) Save each patient to DF
4) Export to excel
"""

# Local data folder for testing
block3dir = pathlib.Path("../../Block3_Local/Data")
# block3dir.mkdir()

# Local dict for holding output excel data
dict_dir = pathlib.Path("../../Block3_Local/Excel_Data/")

# Local plot saving directory
dens_dir = pathlib.Path("../../Block3_Local/Plot_Data")
# dens_dir.mkdir(parents=True, exist_ok=True)

# Local data for reading in .edf files
data_dir = pathlib.Path("../../Block3_Local/Data")
files = pathlib.Path(data_dir).glob('*')

# Local data for reading in night division data
div_data = pathlib.Path("../../Block3_Local/Rec_Times_50.xlsx")

# Read in division data to DataFrame
DivDF = pd.read_excel(div_data)

# Initialize lists for storage
IDs = []
RecTimes = []

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
            rawImport = mne.io.read_raw_edf(file, preload=True)

            name = name.split('.')[0]
            print(name)
            ID = my.get_ID(file)
            print(ID)

            """
            2) Get total recording time
            """
            RecTimes.append(len(rawImport["EEG"][0][0]))
            IDs.append(ID)

    except:
        print("bruh moment")

    """
    3) Save each patient to DF
    """
    RecTimeSeconds = [(time / rawImport.info["sfreq"]) for time in RecTimes]

    df = pd.DataFrame()
    df["EDF_ID"] = IDs
    df["EEG_Time_Samples"] = RecTimes
    df["EEG_Time_Seconds"] = RecTimeSeconds

    """
    4) Export to excel
    """
    df.to_excel("test.xlsx")
