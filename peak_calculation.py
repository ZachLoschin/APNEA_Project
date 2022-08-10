from importlib.resources import files
from PythonCode import My_Funcs as my
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne
import scipy

''''
Disclaimer: This code is mainly copied from Zachary's code.

What this code does:
    0. Create directories
    1. Read archives
        a. Raw data import
        b. Creation of our data dictionary
        c. Split the data by the night vector
    2. YASA sleep scoring (EEG + EOG)
        a. Yasa spindle detection
        b. Noise spindle elimination
    3. Artifact removal
        a. Create label vec with artifact locations as Nan)
        b. By arousals (using beta band)
    4. Filter
        a. Band pass filter the EEG data (10-16 Hz)
        b. Upper Beta pass filter to graph (20-50 Hz)
    5. Select only N2 and N3 of the Sleep Scoring
    6. Do PSD (IRASA)
        a. All band
        b. Only slow spindles (9 - 12.5 Hz)
        c. Only fast spindles (12.5 - 16 Hz)
'''

'''
0. Create directories
'''

# Local data folder for testing
test_dir = pathlib.Path("../Apnea_Local/Data")
test_dir.mkdir()

# Local dict for holding output excel data
dict_dir = pathlib.Path("../Apnea_Local/Excel_Data/")

# Local plot saving directory
dens_dir = pathlib.Path("../Apnea_Local/Plot_Data")
dens_dir.mkdir(parents=True, exist_ok=True)

# Local data for reading in .edf files
data_dir = pathlib.Path("../Apnea_Local/Data")
files = pathlib.Path(data_dir).glob('*')

# Local data for reading in night division data
div_data = pathlib.Path("../Block3_Local/Rec_Times_50.xlsx")

# Read in division data to DataFrame
DivDF = pd.read_excel(div_data)

# '''
# Read archives (PSD_Confirmation.py)
# '''

# file_dir = pathlib.Path('Z:/ResearchHome/ClusterHome/asanch24/APNEA/APNEA Raw Files/Test_EDF/').glob('*')


# for filename in file_dir:

#     """
#     2) Raw data import
#     """
#     split_array = str(filename).split('\\')
#     name = split_array[-1]

#     rawImport = mne.io.read_raw_edf(filename, preload=True)

#     my.my_plot(rawImport["EEG"][0][0], rawImport["EEG"][1], "Raw Import Data", 1)

#     win = int(4 * rawImport.info["sfreq"])

#     freqs, psd = scipy.signal.welch(rawImport["EEG"][0][0], rawImport.info["sfreq"], nperseg=win)

#     print("Plotting PSD")
#     plt.clf()
#     plt.plot(freqs, psd, 'k', lw=2)
#     plt.fill_between(freqs, psd, cmap='Spectral')
#     plt.xlim(1, 30)
#     plt.yscale('log')
#     plt.title('Raw Import PSD')
#     plt.xlabel('Frequency (Hz)')
#     plt.ylabel('PSD Log($uV^2$/Hz)')
#     plt.show()

'''
1. Read archives
'''

"""
a) Raw data import
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
b) Creation of our data dictionary
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
c) Split the data by the night vector
"""
# Get the recording times for night 1 and 2
DivDF_Patient = DivDF.loc[DivDF["EDF_ID"] == ID]

Time_N1 = float(DivDF_Patient.iloc[0]["Rec_Time_N1"][0:3])  # in hours
Time_N2 = float(DivDF_Patient.iloc[0]["Rec_Time_N2"][0:3])  # in hours

# Convert these recording times to seconds then to samples
sample_n1 = (Time_N1 * 3600) * data["fs"]
sample_n2 = (Time_N2 * 3600) * data["fs"]

# If there is left over in the middle, take midpoint
if sample_n2 + sample_n1 < len(data["EEG"]):
    gap = len(data["EEG"]) - sample_n2 + sample_n1

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

'''
YASA sleep scoring (EEG + EOG (LEOG, REOG))
'''

"""
a) Yasa spindle detection
b) Noise spindle elimination
"""
# This function detects the spindles and does our artifact based elimination
Spindles_N1 = my.detect_spindles(Data_N1)
Spindles_N2 = my.detect_spindles(Data_N2)

'''
Detection and removal of artifacts
'''

# See in the signal any point that goes above 250uV
# and convert it to NaN
"""
a) Create label vec with artifact locations as NaN)
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

'''
b) By arousals (using beta band)
'''

# Band pass filter (20-50 Hz)
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

# Root mean square (RMS)

# Mean and STD

# *Everything that is over mean + 2*STD is an artifact 
# (Zach uses 10 as an approx)

'''
Select only N2 and N3 of the Sleep Scoring
'''

# Use NaN for Wake, N1 and REM

'''
Do PSD (IRASA)
'''

# All band

# Slow spindles (9 - 12.5 Hz)

# Fast spindles (12.5 - 16 Hz)

# *It may be neccesary to smooth the IRASA curve