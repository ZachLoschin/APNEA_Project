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
2) Use MNE IIR filter to low pass 18Hz cut off
3) Split patient data by night
4) Split to .EDF files
5) Save the data to .EDF
"""

# Local data folder for testing
block3dir = pathlib.Path("../Block3_Local/Data")
# block3dir.mkdir()

# Local dict for holding output excel data
dict_dir = pathlib.Path("../Block3_Local/Excel_Data/")

# Local plot saving directory
dens_dir = pathlib.Path("../Block3_Local/Plot_Data")
# dens_dir.mkdir(parents=True, exist_ok=True)

# Local data for reading in .edf files
data_dir = pathlib.Path("../Block3_Local/Data")
files = pathlib.Path(data_dir).glob('*')

# Local data for reading in night division data
div_data = pathlib.Path("../Block3_Local/Rec_Times_50.xlsx")

# Read in division data to DataFrame
DivDF = pd.read_excel(div_data)

for file in files:

    # Setup try for each file to not stop running if one error occurs

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
        2) Use MNE IIR filter
        """
        filteredData = rawImport.filter(l_freq=None, h_freq=18, picks=["EEG"], method='iir')
        eeg = rawImport["EEG"][0][0]

        """
        3) Split the data by the night vector
        """
        # Get the recording times for night 1 and 2
        DivDF_Patient = DivDF.loc[DivDF["EDF_ID"] == ID]

        Time_N1 = float(DivDF_Patient.iloc[0]["Rec_Time_N1"][0:3])  # in hours
        Time_N2 = float(DivDF_Patient.iloc[0]["Rec_Time_N2"][0:3])  # in hours

        # Convert these recording times to seconds then to samples
        sample_n1 = (Time_N1 * 3600) * rawImport.info["sfreq"]
        sample_n2 = (Time_N2 * 3600) * rawImport.info["sfreq"]

        # If there is left over in the middle, take midpoint
        if sample_n2 + sample_n1 < len(eeg):
            gap = len(eeg) - sample_n2 + sample_n1

            # Set sample one to include first half of gap
            sample_n1 = sample_n1 + (0.5 * gap)

            # Set sample 2 to include samples from middle of gap to end
            sample_n2 = len(eeg) - sample_n1

        elif sample_n2 + sample_n1 > len(eeg):

            # Calculate overlap
            overlap = abs(len(eeg) - sample_n1 - sample_n2)

            # Set sample one to exclude half of gap
            sample_n1 = sample_n1 - (0.5 * overlap)

            # Set sample 2 to include samples from middle of overlap to end
            sample_n2 = len(eeg) - sample_n1

        """
        4) Split to .EDF files
        """
        # Split the data into two nights
        Night_1 = rawImport.crop(tmin=0, tmax=(len(rawImport) / rawImport.info["sfreq"]) - 60, include_tmax=False)
        # Night_2 = rawImport.crop(tmin=sample_n1 / rawImport.info["sfreq"],
                                 # tmax=(len(rawImport) / rawImport.info["sfreq"]) - 60, include_tmax=False)

        """
        5) Save the data to .EDF
        """
        # Make filenames
        nameN1 = "%s_N1" % ID
        nameN2 = "%d_N2" % ID

        # Make paths
        pathN1 = dict_dir / nameN1
        pathN2 = dict_dir / nameN2

        # Save .EDF
        Night_1.export(fname=pathN1, fmt='edf')
        # Night_2.export(fname=pathN2, fmt='edf')
