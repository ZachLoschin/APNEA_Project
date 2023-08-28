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
###########################################################################
# Changes To Be Made: 1) Standard deviation based beta noise rejection
#                     2) Test the use of NREM2 and NREM3 only in Yasa.Spindle_Detect() -- DONE
#                     3) Record the Spindle Density in the Output Files
#                           - I feel this may be easier to do afterwards though, since the
#                             output files are excel files with individual rows for each spindle.
###########################################################################

# Data directory for official runs
data_dir = pathlib.Path("./Block1_Output/FIF_Files/")  # 

# Directory for official running
pipdir = pathlib.Path("./Block2_Output_June15/Spindles_Scoring/")  # 
pipdir.mkdir(parents=True, exist_ok=True)

# Shared directory for official runs
dict_dir = pathlib.Path("./Block2_Output_June15/Spindles_Scoring/DetectedSpindles_Scoring/")  # 
dict_dir.mkdir(parents=True, exist_ok=True)

noise_dir = pathlib.Path("./Block2_Output_June15/Spindles_Scoring/DetectedNoise/")  # 
noise_dir.mkdir(parents=True, exist_ok=True)

# Official error directory
error_dir = pathlib.Path("./Block2_Output_June15/Spindles_Scoring/Error_Storage/")  # 
error_dir.mkdir(parents=True, exist_ok=True)

# Set up files generator for the for loop
files = pathlib.Path(data_dir).glob('*_Night2.fif')
#files = pathlib.Path(data_dir).glob('*288*.fif')

N2D = []
N3D = []
N23D = []
IDS = []

for file in files:

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
            print(night)
            
            """
            7) Load hypnogram before loading file to not waste time if hypno doesnt exist
            """
            #filename = "%s_" % ID
            #print(filename)
            #filename = str(data_dir) + "/Hypnograms/"+ filename + "%s.npy" % night
            #print(filename)
            #hypno = np.load(filename,allow_pickle=True)   
            
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
            3) Artifact removal (create label vec with artifact locations as Nan)
            """
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
            7) Load hypnogram
            """
            #filename = "%s_" % ID
            #print(filename)
            #filename = str(data_dir) + "/Hypnograms/"+ filename + "%s.npy" % night
            #print(filename)
            #hypno = np.load(filename,allow_pickle=True)   
            
                
            """
            8) Yasa spindle detection
            9) Noise spindle elimination
            """
            # Convert the hypnograms to numbers
            HypnoEnum = my.hypno_to_plot_art(hypno)
            print(len(HypnoEnum))
            print("*************")
            
            # Upsample the Hypnogram to be the same length as the data array
            hypnoEnumUpsampled = my.upsample_hypno_to_data(HypnoEnum, data)
            
            
            # Detect spindles
            spindles, spindlesFlatThresh, noise = my.detect_spindles(data, hypnoEnumUpsampled, night=1, samples1=0)
            
            """
            10) Spectrogram analysis
            """
            # spindles = my.time_frequency_analysis(data, spindles)

            """
            11) Save spindle data to excel
            """
            print("Saving...")
            # Saving no beta rejection spindles
            n1File = "Spindle_%s_" % ID
            n1File = n1File + "%s.xlsx" % night
            n1Path = dict_dir / n1File
            spindles.to_excel(n1Path)
            
            try:
                noiseFile = f"Beta_Noise_{ID}_"
                noiseFile = f"{noiseFile}{night}.csv"
                noisePath = noise_dir / noiseFile
                noise.to_csv(noisePath)
            except:
                print("AN ERROR OCCURRED SAVING NOISE")

            """
            12) Calculating NREM Spindle Densities
            """
            NREM2_Density, NREM3_Density, NREM23_Density = my.nrem_densities(spindles, HypnoEnum)
            
            N2D.append(NREM2_Density)
            N3D.append(NREM3_Density)
            N23D.append(NREM23_Density)
            IDS.append(ID)
            
            # with open(f"Densities{ID}.txt", "w") as file:
            #     file.write(f"NREM2 Density: {NREM2_Density}\n")
            #     file.write(f"NREM3 Density: {NREM3_Density}\n")
            #     file.write(f"NREM2/3 Density: {NREM23_Density}\n")
            
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
densities.to_excel("Densities.xlsx")

