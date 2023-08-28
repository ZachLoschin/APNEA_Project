print("SLOW WAVE DETECTION CODE RUNNING...")
import pathlib
import My_Funcs as my
import pandas as pd
import mne
import yasa
import numpy as np
import matplotlib.pyplot as plt
import os
import h5py


###########################################################################
"""
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Sitaram Group 
APNEA Project Summer 2023
Andrea Sanchez Corzo & Zachary Loschinskey

Description: Code that completes preprocessing, spindle detection, and postprocessing.
Inputs: (1) Folder of .fif files in which to detect spindles.
Outputs: (2) Folder of an excel file with spindle detections and charactistics for each .fif file input.
"""

# Data directory for official runs
data_dir = pathlib.Path("./Block1_Output/FIF_Files/")

# Directory for official running
pipdir = pathlib.Path("./SW_Output_June15/SW/")  # 
pipdir.mkdir(parents=True, exist_ok=True)

# Shared directory for official runs
dict_dir = pathlib.Path("./SW_Output_June15/SW/DetectedSW/")  # 
dict_dir.mkdir(parents=True, exist_ok=True)

noise_dir = pathlib.Path("./SW_Outpu_June15/SW/DetectedNoise/")  # 
noise_dir.mkdir(parents=True, exist_ok=True)

# Official error directory
error_dir = pathlib.Path("./SW_Output_June15/SW/Error_Storage/")  # 
error_dir.mkdir(parents=True, exist_ok=True)

# Set up files generator for the for loop
files = pathlib.Path(data_dir).glob('*_Night2.fif')
#files = pathlib.Path(data_dir).glob('*288*.fif')

N2D = []
N3D = []
N23D = []
IDS = []
count = 0

for file in files:
    count+=1 
    # Setup try for each file to not stop running if one error occurs
    try:
        with open(file, 'rb') as f:
            
            """
            1) Load data
            """ 
            # Extract file information
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
            namee = aa[0]
            print(namee)
            ID = int(namee[-3:-1] + (namee[-1]))
            print(ID)
            namenight = aa[1]
            night = namenight.split('.')
            night = night[0]
            print(f"*****************FILE NUMBER: {count}*****************")
            
            """
            7) Load hypnogram before loading file to not waste time if hypno doesnt exist
            """
            
            hypno_path = '/data/all_andreascoring'
            print(hypno_path+os.sep+'psgHypno-%s_Night2.mat'% ID)
            hypno = h5py.File(hypno_path+os.sep+'psgHypno-%s_Night2.mat'% ID,'r') 
            
            print("HYPNO IMPORTED")
            hypno = hypno['dat']
            hypno = np.array(hypno)
            selectedHypno = hypno[:,1]

            # Create a dictionary to map values to strings
            mapping = {0: 'W', 1: 'N1', 2: 'N2', 3: 'N3', 5: 'R'}

            # Replace the values in selectedHypno with the corresponding strings
            # If a value is not in the mapping, replace it with 'W'
            hypno = np.array([mapping.get(x, 'W') for x in selectedHypno])
            print(len(hypno))
            print("*************")

            print("**")
            print(file)
            rawImport = mne.io.read_raw_fif(file, preload=True)
            eeg = rawImport["EEG"][0][0]
            #filteredData = rawImport.filter(l_freq=None, h_freq=18, picks=["EEG"], method='iir')
            

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
            
            print("Freq:")
            print(rawImport.info["sfreq"])

                
            """
            8) Yasa Slow wave detection
            """
            # Convert the hypnograms to numbers
            HypnoEnum = my.hypno_to_plot_art(hypno)
            print(len(HypnoEnum))
            print("*************")
            
            # Upsample the Hypnogram to be the same length as the data array
            hypnoEnumUpsampled = my.upsample_hypno_to_data(HypnoEnum, data)
            
            SW_Summary, ave_sw = my.detect_slow_waves(data, hypnoEnumUpsampled) # , noise
            
            """
            Calculate slow wave densities
            """
            
            NREM2_Density, NREM3_Density, NREM23_Density = my.nrem_densities(SW_Summary, HypnoEnum)
            
            N2D.append(NREM2_Density)
            N3D.append(NREM3_Density)
            N23D.append(NREM23_Density)
            IDS.append(ID)
            
            """
            11) Save Slow wave data to excel
            """
            print("Saving...")
            n1File = "Slow_Wave_%s_" % ID
            n1File = n1File + "%s.xlsx" % night
            n1Path = dict_dir / n1File
            SW_Summary.to_excel(n1Path)
            
            """
            Graph the average slow wave and save it
            """

            plt.plot(ave_sw)
            plt.xlabel('Time (s)')
            plt.ylabel('Normalized Ampliteude (uV)')
            plt.title('Average SW Graph ')
            plt.grid(True)
            plt.savefig(f'./SW_Output/SW/Plots/Slow_Wave_Graph_{ID}_AmpFiltered.png')
            plt.clf()
            
            
            # # Save the beta noise detections
            # try:
            #     noiseFile = f"Beta_Noise_{ID}_"
            #     noiseFile = f"{noiseFile}{night}.csv"
            #     noisePath = noise_dir / noiseFile
            #     noise.to_csv(noisePath)
            # except:
            #     print("AN ERROR OCCURRED SAVING NOISE")
            
    except Exception as e:
        print(str(e))
        print("PROBLEM PROBLEM PROBLEM ***** : ID = %s" % ID)
        error_file = '%s_%s.txt' % (ID, 'ErrorMSG')
        error_path = error_dir / error_file
        with open(error_path, 'w') as file:
            file.write(str(e))

densities = pd.DataFrame()
densities["ID"] = IDS
densities["N2"] = N2D
densities["N3"] = N3D
densities["N23"] = N23D
densities.to_excel("SW_Densities.xlsx")

