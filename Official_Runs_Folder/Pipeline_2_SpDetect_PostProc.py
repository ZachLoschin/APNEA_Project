import pathlib
import My_Funcs as my
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne
import numpy as np

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
    2) Creation of our data dictionary
    3) Artifact removal label vector creation
    4) Band pass filter the EEG_ArtZero data (9-15Hz)
    5) Upper Beta pass filter to graph (20-30 Hz)
    6) Remove artifacts using label vector
    7) Use recording times to find where to split data
    7) Split the data by the night vector
    8) Yasa spindle detection
    9) Noise spindle elimination
    10) Spectrogram analysis
    11) Plot the density and hypnograms
    12) Save spindle data to excel
"""

"""
0) Create Directories
"""

print("Creating directories...")

# Data directory for official runs
data_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/APNEA Raw Files/Subset1/")

# Directory for official running
pipdir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Pipeline2/")
pipdir.mkdir(parents=True, exist_ok=True)

# Shared directory for official runs
dict_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Pipeline2/Excel_Data_All/")
dict_dir.mkdir(parents=True, exist_ok=True)

# Plot directory for saving density graphs
dens_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Pipeline2/Hypnogram_Plots/")
dens_dir.mkdir(parents=True, exist_ok=True)

# Official error directory
error_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Pipeline2/Error_Storage/")
error_dir.mkdir(parents=True, exist_ok=True)


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
div_data = pathlib.Path("../Official_Runs_Folder/CompleteTable2.xlsx")

# Local directory for error storage
error_dir = pathlib.Path("../Block3_Local/Error_Storage")
error_dir.mkdir(parents=True, exist_ok=True)
"""

# Local data for reading in night division data
div_data = pathlib.Path("../Official_Runs_Folder/CompleteTable2.xlsx")

# Read in division data to DataFrame
DivDF = pd.read_excel(div_data)

# Set up files generator for the for loop
files = pathlib.Path(data_dir).glob('*')

# Import the data
for file in files:

    # Setup try for each file to not stop running if one error occurs
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
            7) Use recording times to find where to split data
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
                print("No Nights for patient %s" % ID)
                continue
            elif nights == -1:
                continue
            elif nights == 1:
                # STEPS FOR ONE NIGHT
                """
                8) Yasa spindle detection
                9) Noise spindle elimination
                """
                spindles = my.detect_spindles(data)

                """
                10) Spectrogram analysis
                """
                spindles = my.time_frequency_analysis(data, spindles)

                """
                11) Plot the density and hypnograms
                """
                my.plot_density(rawImport, data, ID, spindles, dens_dir, 1)

                """
                12) Save spindle data to excel
                """
                n1File = "Spindle_%s_N1" % ID
                n1Path = dict_dir / n1File
                spindles.to_excel(n1Path)

            # If the patient has two nights of data
            elif nights == 2:

                """
                7) Split the data by the night vector
                """
                # Get the recording times for night 1 and 2
                Time_N1 = float(DivDF_Patient.iloc[0]["RecordingTime"])  # in hours
                Time_N2 = float(DivDF_Patient.iloc[1]["RecordingTime"])  # in hours

                # Convert these recording times to seconds then to samples
                sample_n1 = (Time_N1 * 3600) * data["fs"]
                sample_n2 = (Time_N2 * 3600) * data["fs"]

                # If there is left over in the middle, take midpoint
                if sample_n2 + sample_n1 < len(data["EEG"]):
                    gap = len(
                        data["EEG"]) - sample_n2 - sample_n1  # Changed the second minus to minus from a plus 7/21/22 ZFL

                    # Set sample one to include first half of gap
                    sample_n1 = sample_n1 + (0.5 * gap)

                    # Set sample 2 to include samples from middle of gap to end
                    sample_n2 = len(data["EEG"]) - sample_n1

                elif sample_n2 + sample_n1 > len(data["EEG"]):

                    # Calculate overlap
                    overlap = abs(len(data["EEG"]) - sample_n1 - sample_n2)

                    # Set sample one to exclude half of gap
                    sample_n1 = sample_n1 - (0.5 * overlap)

                    # Set sample 2 to include samples from middle of overlap to end
                    sample_n2 = len(data["EEG"]) - sample_n1

                # Divide the EEG, eeg filtered, art, and beta vectors into night based
                sample_n1 = round(sample_n1)

                Data_N1 = {}
                Data_N2 = {}

                Data_N1["EEG"] = data["EEG"][0:sample_n1]
                Data_N2["EEG"] = data["EEG"][sample_n1:-1]

                Data_N1["EEG_ArtZero"] = data["EEG_ArtZero"][0:sample_n1]
                Data_N2["EEG_ArtZero"] = data["EEG_ArtZero"][sample_n1:-1]

                Data_N1["ArtZero"] = data["ArtZero"][0:sample_n1]
                Data_N2["ArtZero"] = data["ArtZero"][sample_n1:-1]

                Data_N1["EEG_Beta"] = data["EEG_Beta"][0:sample_n1]
                Data_N2["EEG_Beta"] = data["EEG_Beta"][sample_n1:-1]

                Data_N1["EEG_Filt"] = data["EEG_Filt"][0:sample_n1]
                Data_N2["EEG_Filt"] = data["EEG_Filt"][sample_n1:-1]

                Data_N1["Beta_Labels"] = data["Beta_Labels"][0:sample_n1]
                Data_N2["Beta_Labels"] = data["Beta_Labels"][sample_n1:-1]

                Data_N1["TimeVec"] = data["TimeVec"][0:sample_n1]
                Data_N2["TimeVec"] = data["TimeVec"][sample_n1:-1]

                Data_N1["fs"] = data["fs"]
                Data_N2["fs"] = data["fs"]

                """
                8) Yasa spindle detection
                9) Noise spindle elimination
                """
                # This function detects the spindles and does our artifact based elimination
                Spindles_N1 = my.detect_spindles(Data_N1)
                Spindles_N2 = my.detect_spindles(Data_N2)

                """
                10) Spectrogram analysis
                """
                # print("Completing spectrogram analysis")
                Spindles_N1 = my.time_frequency_analysis(Data_N1, Spindles_N1)
                Spindles_N2 = my.time_frequency_analysis(Data_N2, Spindles_N2)

                """
                11) Plot the density and hypnograms
                """
                print("Plotting density and hypnograms")
                my.plot_density(rawImport, Data_N1, ID, Spindles_N1, dens_dir, 1)
                my.plot_density(rawImport, Data_N2, ID, Spindles_N2, dens_dir, 2)

                """
                12) Save spindle data to excel
                """
                # Saving night 1
                n1File = "Spindle_%s_N1.xlsx" % ID
                n1Path = dict_dir / n1File
                Spindles_N1.to_excel(n1Path)

                # Saving night 2
                n2File = "Spindle_%s_N2.xlsx" % ID
                n2Path = dict_dir / n2File
                Spindles_N2.to_excel(n2Path)

    except:
        print("PROBLEM PROBLEM PROBLEM ***** : ID = %s" % ID)
        error_file = '%s_%s.txt' % (ID, 'ErrorMSG')
        error_path = error_dir / error_file
        with open(error_path, 'w') as e:
            e.write('Error running %s\n' % ID)