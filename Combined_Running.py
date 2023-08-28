print("Combined Running Started...")
import pathlib
import My_Funcs as my
import pandas as pd
import mne
import yasa
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
import os
import h5py

###########################################################################
"""
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Sitaram Group 
APNEA Project Summer 2023
Andrea Sanchez Corzo & Zachary Loschinskey

Description: Code that separates a 2 night .edf file into individual nights and saves each one a its own .fif file.
             Then spindles are detected on the loaded second night of EEG data
             Then spindles ae detected on the loaded second night of EEG data
             
Inputs: (1) data_dir includes all .edf files to be analyzed
        (2) div_data is the complete excel table given by the PSG2 device.

Outputs: (1) Includes two .fif files of the psg data, one for each night.
         (2) An output directory of all the detected spindles and noises.
         (3) An output directory of all the detected slow waves.
         (4) An error directory including all patient error messages.
"""

###########################################################################


"""
Data Directories
"""
print("Setting Up Directories...")
# .EDF file path
data_dir = pathlib.Path("/data/allcases")

# Local table for reading in night division data
div_data = pathlib.Path("./CompleteTable_WithCognitiveData.xlsx")

# Read in division data to DataFrame
DivDF = pd.read_excel(div_data,engine='openpyxl')


"""
Storage Directories for night division part
"""
# Plot directory for Nights
NightSepPlot_dir = pathlib.Path("./Combined_Running/Night_Div/Plots/")
NightSepPlot_dir.mkdir(parents=True, exist_ok=True)

# Save directory for Nights division
NightSep_dir = pathlib.Path("./Combined_Running/Night_Div/FIF_Files/")
NightSep_dir.mkdir(parents=True, exist_ok=True)

# Official error directory
error_dir_night_division = pathlib.Path("./Combined_Running/Night_Div/Error_Storage/")
error_dir_night_division.mkdir(parents=True, exist_ok=True)


"""
Storage Directories for Spindle detection
"""
# Spindle Folder
pipdir_spindles = pathlib.Path("./Combined_Running/Spindles_Data/")
pipdir_spindles.mkdir(parents=True, exist_ok=True)

# Shared directory for official runs
dict_dir_spindles = pathlib.Path("./Combined_Running/Spindles_Data/Detected_Spindles/")
dict_dir_spindles.mkdir(parents=True, exist_ok=True)

noise_dir_spindles = pathlib.Path("./Combined_Running/Spindles_Data/Detected_Noise/")
noise_dir_spindles.mkdir(parents=True, exist_ok=True)

# Official error directory
error_dir_spindles = pathlib.Path("./Combined_Running/Spindles_Data/Error_Storage/")
error_dir_spindles.mkdir(parents=True, exist_ok=True)


"""
Storage Directories for Slow wave detection
"""
# Directory for official running
pipdir_sw = pathlib.Path("./Combined_Running/SW_Data/")
pipdir_sw.mkdir(parents=True, exist_ok=True)

# Shared directory for official runs
dict_dir_sw = pathlib.Path("./Combined_Running/SW_Data/Detected_SW/")
dict_dir_sw.mkdir(parents=True, exist_ok=True)

noise_dir_sw = pathlib.Path("./Combined_Running/SW_Data/Detected_Noise/")
noise_dir_sw.mkdir(parents=True, exist_ok=True)

# Official error directory
error_dir_sw = pathlib.Path("./Combined_Running/SW_Data/Error_Storage/")
error_dir_sw.mkdir(parents=True, exist_ok=True)

# Plots of average slow wave
plot_dir_sw = pathlib.Path("./Combined_Running/SW_Data/Plots/")
plot_dir_sw.mkdir(parents=True, exist_ok=True)


"""
Storage lists for participant items
"""
N2D = []
N3D = []
N23D = []

N2D_SW = []
N3D_SW = []
N23D_SW = []

IDs = []
AllIDs = []

EndTimeN1 = []
StartTimeN2 = []

"""
Setup file generator for the for loop
"""
files = pathlib.Path(data_dir).glob('*137_Export.edf')
            
for file in files:
    """
    Try block for spindle detection
    """
    try:

        """
        Get the ID and the night number
        """
        print("Entering Spindle Block...")
        """
        Load hypnogram 
        """
        hypno_path = '/data/all_andreascoring'
        print(hypno_path+os.sep+'psgHypno-%s_Night2.mat'% ID)
        hypno = h5py.File(hypno_path+os.sep+'psgHypno-%s_Night2.mat'% ID,'r') 
        
        hypno = hypno['dat']
        hypno = np.array(hypno)
        selectedHypno = hypno[:,1]

        # Create a dictionary to map values to strings
        mapping = {0: 'W', 1: 'N1', 2: 'N2', 3: 'N3', 5: 'R'}

        # Replace the values in selectedHypno with the corresponding strings
        # If a value is not in the mapping, replace it with 'W'
        hypno = np.array([mapping.get(x, 'W') for x in selectedHypno])
        print(len(hypno))

        eeg = night_2["EEG"][0][0]


        """
        Creation of our data dictionary
        """
        print("Creating dict...")
        # Create epoch vector
        epochVec = my.create_epochs(night_2["EEG"][0][0], night_2.info["sfreq"], 30)

        # Create epoch time vector
        epochTimeVec = my.create_epochs(night_2["EEG"][1], night_2.info["sfreq"], 30)

        # Create Dictionary for organization
        data = my.create_dict(night_2["EEG"][0][0], night_2.info["sfreq"], night_2["EEG"][1], epochVec,
                              epochTimeVec)

        """
        Artifact removal (create label vec with artifact locations as Nan)
        """
        print("Creating artifact label vector...")
        data["ArtZero"] = np.zeros(len(data["EEG"]))
        for i in range(len(data["ArtZero"])):
            if abs(data["EEG"][i]) >= 250:
                data["ArtZero"][i] = np.nan

        """
        Band pass filter the EEG data (10-16 Hz)
        """
        print("Bandpass filtering...")
        data["EEG_Filt"] = my.butter_bandpass_filter(data["EEG"], 10, 16, data["fs"], order=5)

        """
        Upper Beta pass filter to graph (20-50 Hz)
        """
        print("Beta pass filtering...")
        data["EEG_Beta"] = my.butter_bandpass_filter(data["EEG"], 20, 50, data["fs"], order=5)
        data["Beta_Labels"] = np.zeros(len(data["EEG_Beta"]))

        # For any threshold event, change the beta label vec to 1
        for i in range(len(data["EEG_Beta"])):
            if data["EEG_Beta"][i] > 10:
                data["Beta_Labels"][i - 64:i + 64] = 1

        """
        Remove artifacts using the label vector
        """
        print("Removing artifacts...")
        data["EEG_ArtZero"] = data["EEG"]
        for i in range(len(data["EEG"])):
            if np.isnan(data["ArtZero"][i]):
                data["EEG_ArtZero"][i] = 0
                data["EEG_Filt"][i] = 0
                data["EEG_Beta"][i] = 0
        
        """
        Yasa spindle detection and noise elimination
        """
        # Convert the hypnograms to numbers
        HypnoEnum = my.hypno_to_plot_art(hypno)

        # Upsample the Hypnogram to be the same length as the data array
        hypnoEnumUpsampled = my.upsample_hypno_to_data(HypnoEnum, data)
        
        print("Detecting Spindles...")
        # Detect spindles
        spindles, noise = my.detect_spindles(data, hypnoEnumUpsampled, night=2, samples1=0)

        night = 2
        
        """
        11) Save spindle data to excel
        """
        print("Saving Spindle Data...")
        n1File = "Spindle_%s_" % ID
        n1File = n1File + "%s.xlsx" % night
        n1Path = dict_dir_spindles / n1File
        spindles.to_excel(n1Path)

        noiseFile = f"Beta_Noise_{ID}_"
        noiseFile = f"{noiseFile}{night}.csv"
        noisePath = noise_dir_spindles / noiseFile
        noise.to_csv(noisePath)
        
        """
        12) Calculating NREM Spindle Densities
        """
        print("Calculating Spindle Density...")
        NREM2_Density, NREM3_Density, NREM23_Density = my.nrem_densities(spindles, HypnoEnum)

        N2D.append(NREM2_Density)
        N3D.append(NREM3_Density)
        N23D.append(NREM23_Density)
        
    except Exception as e:
        print("_____________________________________")
        error_file = '%s_%s.txt' % (ID, 'ErrorMSG')
        error_path = error_dir_spindles / error_file
        with open(error_path, 'w') as file:
            file.write(str(e))
        continue
    
    
    """
    Try block for slow wave detection 
    """    
    try:
        print("Entering Slow Wave Block...")
        """
        Yasa Slow wave detection
        """
        # Upsample the Hypnogram to be the same length as the data array
        hypnoEnumUpsampled = my.upsample_hypno_to_data(HypnoEnum, data)
        
        print("Detecting Slow Waves...")
        SW_Summary, ave_sw = my.detect_slow_waves(data, hypnoEnumUpsampled)
        

        """
        Calculate slow wave densities
        """
        print("Calculating Slow Wave Densities...")
        NREM2_Density, NREM3_Density, NREM23_Density = my.nrem_densities(SW_Summary, HypnoEnum)

        N2D_SW.append(NREM2_Density)
        N3D_SW.append(NREM3_Density)
        N23D_SW.append(NREM23_Density)
        
        
        """
        11) Save Slow wave data to excel
        """
        print("Saving Slow Wave Data...")
        n1File = "Slow_Wave_%s_" % ID
        n1File = n1File + "%s.xlsx" % night
        n1Path = dict_dir_sw / n1File
        SW_Summary.to_excel(n1Path)
        
        
        """
        Graph the average slow wave and save it
        """
        print("Plotting Average Slow Wave and Saving...")
        plt.plot(ave_sw)
        plt.xlabel('Time (s)')
        plt.ylabel('Normalized Ampliteude (uV)')
        plt.title('Average SW Graph ')
        plt.grid(True)
        plt.savefig(f'./Combined_Running/SW_Data/Plots/Slow_Wave_Graph_{ID}_AmpFiltered.png')
        plt.clf()
        
    except Exception as e:
        print("##################################")
        error_file = '%s_%s.txt' % (ID, 'ErrorMSG')
        error_path = error_dir_sw / error_file
        with open(error_path, 'w') as file:
            file.write(str(e))
        continue

"""
Save the night division table
"""
print("Saving Night Division Table...")
df_NightTime = pd.DataFrame({"ID":AllIDs,"EndTimeN1":EndTimeN1,"StartTimeN2":StartTimeN2})
filename = 'NightDiv.xlsx'
nightDivPath = pathlib.Path("./Combined_Running/Night_Div/")
filepath = nightDivPath / filename
df_NightTime.to_excel(filepath)


"""
Save the Spindle Density Tables
"""
print("Saving Spindle Density Table...")
densities = pd.DataFrame()
densities["ID"] = IDs
densities["N2"] = N2D
densities["N3"] = N3D
densities["N23"] = N23D

filename = 'Spindle_Densities.xlsx'
spindle_density_path  = pipdir_spindles / filename
densities.to_excel(spindle_density_path)


"""
Save the Slow Wave Density Tables
"""
print("Saving Slow Wave Density Table")
densities_sw = pd.DataFrame()
densities_sw["ID"] = IDs
densities_sw["N2"] = N2D_SW
densities_sw["N3"] = N3D_SW
densities_sw["N23"] = N23D_SW

filename = 'SW_Densities.xlsx'
sw_density_path = pipdir_sw / filename
densities_sw.to_excel(sw_density_path)
