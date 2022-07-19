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
19 July 2022
"""

"""
Description:
    This script is for importing raw .edf file data, completing preprocessing, computing the hypnogram for each
        night for each patient, and saving the generated hypnograms.

Inputs to this .py file are 1) The .edf file directory
                            2) The corresponding sleep division Excel file
                            3) The directory to store the hypnograms
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
Pipline_1 Layout: Import, compute hypnograms, save .pngs
    0) Create directories
    1) Import data
    2) Use recording times to find where to split data
    3) Split the data by night
    4) Compute hypnograms for each night
    5) Plot hypnograms and save to directory
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


# Create dataframe for holding the percent time in each state
StateTimes = pd.DataFrame()
IDPerc = []
WakePercN1 = []
REMPercN1 = []
NREM1PercN1 = []
NREM2PercN1 = []
NREM3PercN1 = []

WakePercN2 = []
REMPercN2 = []
NREM1PercN2 = []
NREM2PercN2 = []
NREM3PercN2 = []

# For each .edf file
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

        eeg = rawImport["EEG"][0][0]
        filteredData = rawImport.filter(l_freq=None, h_freq=18, picks=["EEG"], method='iir')

        """
        2) Use recording times to find where to split data
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
        3) Split up by night
        """
        # Copy raw import to second one for cropping night 2
        rawImport2 = rawImport.copy()
        # Split the data into two nights
        Night_1 = rawImport.crop(tmin=0, tmax=sample_n1 / rawImport.info["sfreq"], include_tmax=False)
        Night_2 = rawImport2.crop(tmin=sample_n1 / rawImport.info["sfreq"],
                                  tmax=(len(rawImport2) / rawImport.info["sfreq"]) - 60, include_tmax=False)

        """
        4) Compute hypnograms for each night
        """
        # Calculate sleep stages using EEG and EOG channels on the filtered data
        print("Sleep staging...")
        Night1_sls = yasa.SleepStaging(raw=Night_1, eeg_name="EEG", eog_name="LEOG")
        Night2_sls = yasa.SleepStaging(raw=Night_2, eeg_name="EEG", eog_name="LEOG")

        # Get hypno objects
        Night1_Hypno = Night1_sls.predict()
        Night2_Hypno = Night2_sls.predict()

        # Convert the hypnograms to numbers
        Night1_HypnoEnum = my.hypno_to_plot_art(Night1_Hypno)
        Night2_HypnoEnum = my.hypno_to_plot_art(Night2_Hypno)

        """
        5) Plot the hypnograms and save them to directory
        """
        # Create filenames for saving figures
        Night1_File = "%s_Night1_Hypno.png" % ID
        Night2_File = "%s_Night2_Hypno.png" % ID

        # Create paths for saving figures
        Night1_Path = dens_dir / Night1_File
        Night2_Path = dens_dir / Night2_File

        # Plot and save hypnogram for night 1
        plt.plot(Night1_HypnoEnum)

        plt.savefig(Night1_Path)
        plt.clf()

        # Plot and save hypnogram for night 2
        plt.plot(Night2_HypnoEnum)

        plt.savefig(Night2_Path)
        plt.clf()
        print("Done")

        """
        6) Save percent time in each state
        """
        IDPerc.append(ID)
        WakePercN1.append(Night1_HypnoEnum.count(4) / len(Night1_HypnoEnum))
        REMPercN1.append(Night1_HypnoEnum.count(3) / len(Night1_HypnoEnum))
        NREM1PercN1.append(Night1_HypnoEnum.count(2) / len(Night1_HypnoEnum))
        NREM2PercN1.append(Night1_HypnoEnum.count(1) / len(Night1_HypnoEnum))
        NREM3PercN1.append(Night1_HypnoEnum.count(0) / len(Night1_HypnoEnum))

        WakePercN2.append(Night2_HypnoEnum.count(4) / len(Night2_HypnoEnum))
        REMPercN2.append(Night2_HypnoEnum.count(3) / len(Night2_HypnoEnum))
        NREM1PercN2.append(Night2_HypnoEnum.count(2) / len(Night2_HypnoEnum))
        NREM2PercN2.append(Night2_HypnoEnum.count(1) / len(Night2_HypnoEnum))
        NREM3PercN2.append(Night2_HypnoEnum.count(0) / len(Night2_HypnoEnum))


# Outside patient loop
StateTimes["IDs"] = IDPerc

StateTimes["Wake_Percent_Night1"] = WakePercN1
StateTimes["Wake_Percent_Night2"] = WakePercN2

StateTimes["REM_Percent_Night1"] = REMPercN1
StateTimes["REM_Percent_Night2"] = REMPercN2

StateTimes["NREM1_Percent_Night1"] = NREM1PercN1
StateTimes["NREM1_Percent_Night2"] = NREM1PercN2

StateTimes["NREM2_Percent_Night1"] = NREM2PercN1
StateTimes["NREM2_Percent_Night2"] = NREM2PercN2

StateTimes["NREM3_Percent_Night1"] = NREM3PercN1
StateTimes["NREM3_Percent_Night2"] = NREM3PercN2

# Save to Excel file
ExcelFile = "StatePercents.xlsx"
ExcelPath = dens_dir / ExcelFile
StateTimes.to_excel(ExcelPath)
