# Required Libraries
import pandas as pd
import numpy as np
import openpyxl
import pathlib
import h5py
import os

print("Started...")

"""
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Sitaram Group 
APNEA Project Summer 2023
Andrea Sanchez Corzo & Zachary Loschinskey

Description: Code that calculates spindle and slow wave features and extracts parameters of interest form the polysomnography table
Inputs: (1) Folder of spindle object excel files from Block2
        (2) Folder of slow wave object excel files from Block 4
Outputs: (1) Folder of polysomn complete excel file with spindle and slow wave features
"""

"""
Setup Folders and Paths
"""

# Complete Polysomnography table
complete_table_path = pathlib.Path("combinedData_2023-07-14.xlsx")

age_table_path = pathlib.Path("combinedData_2023-07-14.xlsx")
# Spindle tables path
spindle_folder_path = pathlib.Path("./Combined_Running/Spindles_Data/Detected_Spindles/")

# Slow wave tables path
sw_folder_path = pathlib.Path("./Combined_Running/SW_Data/Detected_SW/")

# Folder Creation
final_table_path = pathlib.Path("./Combined_Running/Final_Table/")
final_table_path.mkdir(parents=True, exist_ok=True)

error_dir = pathlib.Path("./Combined_Running/Final_Table/Error_Storage/")
error_dir.mkdir(parents=True, exist_ok=True)

# Import Tables
complete_table = pd.read_excel(complete_table_path,engine='openpyxl')

# Table with age on it
age_table = pd.read_excel(age_table_path, engine='openpyxl')



"""
Setup Lists to Hold Spindle Features for final table
"""
# Holds Fast+Slow Spindle Features Combined
mean_Spindle_RelPower_NREM_All = []
mean_Spindle_Amplitude_NREM_All = []
mean_Spindle_Frequency_NREM_All = []
mean_Spindle_Duration_NREM_All = []

mean_Spindle_Duration_N2_All = []
mean_Spindle_Amplitude_N2_All = []
mean_Spindle_RelPower_N2_All = []
mean_Spindle_Frequency_N2_All = []

mean_Spindle_Duration_N3_All = []
mean_Spindle_Amplitude_N3_All = []
mean_Spindle_RelPower_N3_All = []
mean_Spindle_Frequency_N3_All = []

std_Spindle_Duration_NREM_All = []
std_Spindle_Amplitude_NREM_All = []
std_Spindle_RelPower_NREM_All = []
std_Spindle_Frequency_NREM_All = []

std_Spindle_Duration_N2_All = []
std_Spindle_Amplitude_N2_All = []
std_Spindle_RelPower_N2_All = []
std_Spindle_Frequency_N2_All = []

std_Spindle_Duration_N3_All = []
std_Spindle_Amplitude_N3_All = []
std_Spindle_RelPower_N3_All = []
std_Spindle_Frequency_N3_All = []

# Holds Slow Spindle Features Only
mean_Slow_Spindle_RelPower_NREM_All = []
mean_Slow_Spindle_Amplitude_NREM_All = []
mean_Slow_Spindle_Frequency_NREM_All = []
mean_Slow_Spindle_Duration_NREM_All = []

mean_Slow_Spindle_Duration_N2_All = []
mean_Slow_Spindle_Amplitude_N2_All = []
mean_Slow_Spindle_RelPower_N2_All = []
mean_Slow_Spindle_Frequency_N2_All = []

mean_Slow_Spindle_Duration_N3_All = []
mean_Slow_Spindle_Amplitude_N3_All = []
mean_Slow_Spindle_RelPower_N3_All = []
mean_Slow_Spindle_Frequency_N3_All = []

std_Slow_Spindle_Duration_NREM_All = []
std_Slow_Spindle_Amplitude_NREM_All = []
std_Slow_Spindle_RelPower_NREM_All = []
std_Slow_Spindle_Frequency_NREM_All = []

std_Slow_Spindle_Duration_N2_All = []
std_Slow_Spindle_Amplitude_N2_All = []
std_Slow_Spindle_RelPower_N2_All = []
std_Slow_Spindle_Frequency_N2_All = []

std_Slow_Spindle_Duration_N3_All = []
std_Slow_Spindle_Amplitude_N3_All = []
std_Slow_Spindle_RelPower_N3_All = []
std_Slow_Spindle_Frequency_N3_All = []

# Holds Fast Spindle Features Only
mean_Fast_Spindle_Amplitude_NREM_All = []
mean_Fast_Spindle_RelPower_NREM_All = []
mean_Fast_Spindle_Frequency_NREM_All = []
mean_Fast_Spindle_Duration_NREM_All = []

mean_Fast_Spindle_Duration_N2_All = []
mean_Fast_Spindle_Amplitude_N2_All = []
mean_Fast_Spindle_RelPower_N2_All = []
mean_Fast_Spindle_Frequency_N2_All = []

mean_Fast_Spindle_Duration_N3_All = []
mean_Fast_Spindle_Amplitude_N3_All = []
mean_Fast_Spindle_RelPower_N3_All = []
mean_Fast_Spindle_Frequency_N3_All = []

std_Fast_Spindle_Duration_NREM_All = []
std_Fast_Spindle_Amplitude_NREM_All = []
std_Fast_Spindle_RelPower_NREM_All = []
std_Fast_Spindle_Frequency_NREM_All = []

std_Fast_Spindle_Duration_N2_All = []
std_Fast_Spindle_Amplitude_N2_All = []
std_Fast_Spindle_RelPower_N2_All = []
std_Fast_Spindle_Frequency_N2_All = []

std_Fast_Spindle_Duration_N3_All = []
std_Fast_Spindle_Amplitude_N3_All = []
std_Fast_Spindle_RelPower_N3_All = []
std_Fast_Spindle_Frequency_N3_All = []

"""
Setup lists to hold slow wave features for final table
"""
# Mean storage
sw_Mean_Duration = []
sw_Mean_ValNegPeak = []
sw_Mean_ValPosPeak = []
sw_Mean_PTP = []
sw_Mean_Slope = []
sw_Mean_Frequency = []
sw_Mean_SigmaPeak = []
sw_Mean_PhaseAtSigmaPeak = []
sw_Mean_ndPAC = []

# Standard deviation storage
sw_std_Duration = []
sw_std_ValNegPeak = []
sw_std_ValPosPeak = []
sw_std_PTP = []
sw_std_Slope = []
sw_std_Frequency = []
sw_std_SigmaPeak = []
sw_std_PhaseAtSigmaPeak = []
sw_std_ndPAC = []

# Misc
IDs = []

# I don't know what these are referring to
Conds_NREM ={}
Conds_N2 ={}
Conds_N3 ={}

"""
Storage Vectors for Complete Table Features
"""
AHINonREM = []
AHIOverall = []
EDF_ID = []
Age = []
Sex = []
PulseRateMean = []
PulseRateStDev = []
PulseRateMax = []
PulseRateMin = []
HypopneaOverallIndex = []
ApneaOverallIndex = []
RDIOverall = []
RDINonREM = []
ODI4Overall = []
ODI3Overall = []
SpO2Mean = []
SpO2SD = []
SpO2Min = []
SpO2Max = []
sBMI = []

"""
Density Storage Vectors
"""
Spindle_NREM2_Density = []
Spindle_NREM3_Density = []
Spindle_NREM23_Density = []

SW_NREM2_Density = []
SW_NREM3_Density = []
SW_NREM23_Density = []


print("Storage Arrays Created...")

"""
Get Features from each participant's spindle excel file
"""

files = pathlib.Path(spindle_folder_path).glob('*.xlsx')
print("Spindle Folder Path Found...")
print("Calculating Features...")
count = 0
# try:
for file in files:
    count +=1
    # D:\Zach_Code\Combined_Running\Spindles_Data\Detected_Spindles\Spindle_16_2.xlsx
    # Extract the patient ID from the file name
    print("DOES THIS EVEN WORK")
    print(str(file))
    parts = str(file).split("_")
    print("PARTS")
    print(parts)

    night = int(parts[-1][0])
    print(night)

    ID = int(parts[-2])
    print(ID)

    
    
    # Read the Spindle File
    spindle_df = pd.read_excel(file, engine='openpyxl')
    
    # Define the slow wave file path for the this participant ID
    sw_file = f'Slow_Wave_{ID}_{night}.xlsx'
    sw_path = sw_folder_path / sw_file
    
    # Read the slow wave file
    sw_df = pd.read_excel(sw_path, engine='openpyxl')

    """
    Slow wave mean calculations
    """
    sw_Mean_Duration.append(sw_df["Duration"].mean())
    sw_Mean_ValNegPeak.append(sw_df["ValNegPeak"].mean())
    sw_Mean_ValPosPeak.append(sw_df["ValPosPeak"].mean())
    sw_Mean_PTP.append(sw_df["PTP"].mean())
    sw_Mean_Slope.append(sw_df["Slope"].mean())
    sw_Mean_Frequency.append(sw_df["Frequency"].mean())
    sw_Mean_SigmaPeak.append(sw_df["SigmaPeak"].mean())
    sw_Mean_PhaseAtSigmaPeak.append(sw_df["PhaseAtSigmaPeak"].mean())
    sw_Mean_ndPAC.append(sw_df["ndPAC"].mean())
    
    """
    Slow wave std calculations
    """
    sw_std_Duration.append(sw_df["Duration"].std())
    sw_std_ValNegPeak.append(sw_df["ValNegPeak"].std())
    sw_std_ValPosPeak.append(sw_df["ValPosPeak"].std())
    sw_std_PTP.append(sw_df["PTP"].std())
    sw_std_Slope.append(sw_df["Slope"].std())
    sw_std_Frequency.append(sw_df["Frequency"].std())
    sw_std_SigmaPeak.append(sw_df["SigmaPeak"].std())
    sw_std_PhaseAtSigmaPeak.append(sw_df["PhaseAtSigmaPeak"].std())
    sw_std_ndPAC.append(sw_df["ndPAC"].std())
    
    
    
    
    """
    Slow+Fast Spindles Combined
    """
    # Calculate the Values from the table and append them to storage arrays
    # Slow and Fast n2n3 Spindle Data
    mean_Spindle_RelPower_NREM_All.append(spindle_df['RelPower'].mean())
    mean_Spindle_Amplitude_NREM_All.append(spindle_df['Amplitude'].mean())
    mean_Spindle_Frequency_NREM_All.append(spindle_df['Frequency'].mean())
    mean_Spindle_Duration_NREM_All.append(spindle_df['Duration'].mean())

    std_Spindle_RelPower_NREM_All.append(spindle_df['RelPower'].std())
    std_Spindle_Amplitude_NREM_All.append(spindle_df['Amplitude'].std())
    std_Spindle_Frequency_NREM_All.append(spindle_df['Frequency'].std())
    std_Spindle_Duration_NREM_All.append(spindle_df['Duration'].std())
    
    # Slow and Fast n2 Spindle Data
    mean_Spindle_Duration_N2_All.append(spindle_df.loc[spindle_df['Stage'] == 2, 'Duration'].mean())
    mean_Spindle_Amplitude_N2_All.append(spindle_df.loc[spindle_df['Stage'] == 2, 'Amplitude'].mean())
    mean_Spindle_RelPower_N2_All.append(spindle_df.loc[spindle_df['Stage'] == 2, 'RelPower'].mean())
    mean_Spindle_Frequency_N2_All.append(spindle_df.loc[spindle_df['Stage'] == 2, 'Frequency'].mean())

    std_Spindle_Duration_N2_All.append(spindle_df.loc[spindle_df['Stage'] == 2, 'Duration'].std())
    std_Spindle_Amplitude_N2_All.append(spindle_df.loc[spindle_df['Stage'] == 2, 'Amplitude'].std())
    std_Spindle_RelPower_N2_All.append(spindle_df.loc[spindle_df['Stage'] == 2, 'RelPower'].std())
    std_Spindle_Frequency_N2_All.append(spindle_df.loc[spindle_df['Stage'] == 2, 'Frequency'].std())
    
    
    # Slow and Fast n3 Spindle Data
    mean_Spindle_Duration_N3_All.append(spindle_df.loc[spindle_df['Stage'] == 3, 'Duration'].mean())
    mean_Spindle_Amplitude_N3_All.append(spindle_df.loc[spindle_df['Stage'] == 3, 'Amplitude'].mean())
    mean_Spindle_RelPower_N3_All.append(spindle_df.loc[spindle_df['Stage'] == 3, 'RelPower'].mean())
    mean_Spindle_Frequency_N3_All.append(spindle_df.loc[spindle_df['Stage'] == 3, 'Frequency'].mean())

    std_Spindle_Duration_N3_All.append(spindle_df.loc[spindle_df['Stage'] == 3, 'Duration'].std())
    std_Spindle_Amplitude_N3_All.append(spindle_df.loc[spindle_df['Stage'] == 3, 'Amplitude'].std())
    std_Spindle_RelPower_N3_All.append(spindle_df.loc[spindle_df['Stage'] == 3, 'RelPower'].std())
    std_Spindle_Frequency_N3_All.append(spindle_df.loc[spindle_df['Stage'] == 3, 'Frequency'].std())
    
    """
    Slow Spindles
    """
    slow_spindle_df = spindle_df[(spindle_df['Frequency'] <= 12.5)]
    
    # Slow Spidle n2n3 data
    mean_Slow_Spindle_RelPower_NREM_All.append(slow_spindle_df['RelPower'].mean())
    mean_Slow_Spindle_Amplitude_NREM_All.append(slow_spindle_df['Amplitude'].mean())
    mean_Slow_Spindle_Frequency_NREM_All.append(slow_spindle_df['Frequency'].mean())
    mean_Slow_Spindle_Duration_NREM_All.append(slow_spindle_df['Duration'].mean())

    std_Slow_Spindle_RelPower_NREM_All.append(slow_spindle_df['RelPower'].std())
    std_Slow_Spindle_Amplitude_NREM_All.append(slow_spindle_df['Amplitude'].std())
    std_Slow_Spindle_Frequency_NREM_All.append(slow_spindle_df['Frequency'].std())
    std_Slow_Spindle_Duration_NREM_All.append(slow_spindle_df['Duration'].std())

    # Slow Spindle n2 data
    mean_Slow_Spindle_Duration_N2_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 2, 'Duration'].mean())
    mean_Slow_Spindle_Amplitude_N2_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 2, 'Amplitude'].mean())
    mean_Slow_Spindle_RelPower_N2_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 2, 'RelPower'].mean())
    mean_Slow_Spindle_Frequency_N2_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 2, 'Frequency'].mean())
    
    std_Slow_Spindle_Duration_N2_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 2, 'Duration'].std())
    std_Slow_Spindle_Amplitude_N2_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 2, 'Amplitude'].std())
    std_Slow_Spindle_RelPower_N2_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 2, 'RelPower'].std())
    std_Slow_Spindle_Frequency_N2_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 2, 'Frequency'].std())
    
    # Slow Spindle n3 data
    mean_Slow_Spindle_Duration_N3_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 3, 'Duration'].mean())
    mean_Slow_Spindle_Amplitude_N3_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 3, 'Amplitude'].mean())
    mean_Slow_Spindle_RelPower_N3_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 3, 'RelPower'].mean())
    mean_Slow_Spindle_Frequency_N3_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 3, 'Frequency'].mean())

    std_Slow_Spindle_Duration_N3_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 3, 'Duration'].std())
    std_Slow_Spindle_Amplitude_N3_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 3, 'Amplitude'].std())
    std_Slow_Spindle_RelPower_N3_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 3, 'RelPower'].std())
    std_Slow_Spindle_Frequency_N3_All.append(slow_spindle_df.loc[spindle_df['Stage'] == 3, 'Frequency'].std())
    
    """
    Fast Spindles
    """
    fast_spindle_df = spindle_df[(spindle_df['Frequency'] > 12.5)]
    
    # Fast Spidle n2n3 data
    mean_Fast_Spindle_RelPower_NREM_All.append(fast_spindle_df['RelPower'].mean())
    mean_Fast_Spindle_Amplitude_NREM_All.append(fast_spindle_df['Amplitude'].mean())
    mean_Fast_Spindle_Frequency_NREM_All.append(fast_spindle_df['Frequency'].mean())
    mean_Fast_Spindle_Duration_NREM_All.append(fast_spindle_df['Duration'].mean())

    std_Fast_Spindle_RelPower_NREM_All.append(fast_spindle_df['RelPower'].std())
    std_Fast_Spindle_Amplitude_NREM_All.append(fast_spindle_df['Amplitude'].std())
    std_Fast_Spindle_Frequency_NREM_All.append(fast_spindle_df['Frequency'].std())
    std_Fast_Spindle_Duration_NREM_All.append(fast_spindle_df['Duration'].std())

    # Fast Spindle n2 data
    mean_Fast_Spindle_Duration_N2_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 2, 'Duration'].mean())
    mean_Fast_Spindle_Amplitude_N2_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 2, 'Amplitude'].mean())
    mean_Fast_Spindle_RelPower_N2_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 2, 'RelPower'].mean())
    mean_Fast_Spindle_Frequency_N2_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 2, 'Frequency'].mean())
    
    std_Fast_Spindle_Duration_N2_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 2, 'Duration'].std())
    std_Fast_Spindle_Amplitude_N2_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 2, 'Amplitude'].std())
    std_Fast_Spindle_RelPower_N2_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 2, 'RelPower'].std())
    std_Fast_Spindle_Frequency_N2_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 2, 'Frequency'].std())
    
    # Fast Spindle n3 data
    mean_Fast_Spindle_Duration_N3_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 3, 'Duration'].mean())
    mean_Fast_Spindle_Amplitude_N3_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 3, 'Amplitude'].mean())
    mean_Fast_Spindle_RelPower_N3_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 3, 'RelPower'].mean())
    mean_Fast_Spindle_Frequency_N3_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 3, 'Frequency'].mean())

    std_Fast_Spindle_Duration_N3_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 3, 'Duration'].std())
    std_Fast_Spindle_Amplitude_N3_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 3, 'Amplitude'].std())
    std_Fast_Spindle_RelPower_N3_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 3, 'RelPower'].std())
    std_Fast_Spindle_Frequency_N3_All.append(fast_spindle_df.loc[spindle_df['Stage'] == 3, 'Frequency'].std())
    
    """
    Complete Table Feature Extraction
    """
    print("HERE WE ARE")
    participant_table = complete_table[(complete_table["EDF_ID"] == ID) & (complete_table["Night"] == night)]
    print(participant_table)
    print("***")


    AHINonREM.append(participant_table["AHINonREM"].item())

    

    AHIOverall.append(participant_table["AHIOverall"].item())


    EDF_ID.append(participant_table["EDF_ID"].item())

    # Get the age of the participant
    part_age_table = age_table[(age_table["EDF_ID"] == ID) & (age_table["Night"] == night)]

    try:
        Age.append(part_age_table["Age"].item())
    except:
        Age.append(np.nan)
    
    try:
        Sex.append(part_age_table["gender"].item())
    except:
        Sex.append(np.nan)

    PulseRateMean.append(participant_table["PulseRateMean"].item())
    PulseRateStDev.append(participant_table["PulseRateStDev"].item())
    PulseRateMax.append(participant_table["PulseRateMax"].item())
    PulseRateMin.append(participant_table["PulseRateMin"].item())

    HypopneaOverallIndex.append(participant_table["HypopneaOverallIndex"].item())
    ApneaOverallIndex.append(participant_table["ApneaOverallIndex"].item())

    RDIOverall.append(participant_table["RDIOverall"].item())
    RDINonREM.append(participant_table["RDINonREM"].item())

    ODI4Overall.append(participant_table["ODI4Overall"].item())
    ODI3Overall.append(participant_table["ODI3Overall"].item())

    SpO2Mean.append(participant_table["SpO2Mean"].item())
    SpO2SD.append(participant_table["SpO2SD"].item())
    SpO2Min.append(participant_table["SpO2Min"].item())
    SpO2Max.append(participant_table["SpO2Max"].item())
    sBMI.append(participant_table["sBMI"].item())

    """
    Density Calculation
    """
    hypno_path = 'D:/APNEA_project_edfs/ReadyForChecking/'
    hypno = h5py.File(hypno_path+os.sep+'psgHypno-%s_%s.mat'% (ID, night)) 

    hypno = hypno['dat']
    hypno = np.array(hypno)
    selectedHypno = hypno[:,1]

    # Create a dictionary to map values to strings
    mapping = {0: 'W', 1: 'N1', 2: 'N2', 3: 'N3', 5: 'R'}

    # Replace the values in selectedHypno with the corresponding strings
    # If a value is not in the mapping, replace it with 'W'
    hypno = np.array([mapping.get(x, 'W') for x in selectedHypno])

    # Save the number of N2, N3, and N23 epochs
    N2_Count = np.count_nonzero(hypno == "N2")
    N3_Count = np.count_nonzero(hypno == "N3")
    N23_Count = N2_Count + N3_Count

    # Get dataframe for N2 spindles only and N3 spindles only
    N2_Spindles = spindle_df[(spindle_df['Stage']==2)]
    N3_Spindles = spindle_df[(spindle_df['Stage']==3)]

    N2_SW = sw_df[(sw_df["Stage"]==2)]
    N3_SW = sw_df[(sw_df["Stage"]==3)]
    
    # Count number of sw and spindles in each stage
    N2_Spindle_Count = len(N2_Spindles["Stage"])
    N3_Spindle_Count = len(N3_Spindles["Stage"])
    N23_Spindle_Count = N2_Spindle_Count+N3_Spindle_Count

    N2_SW_Count = len(N2_SW["Stage"])
    N3_SW_Count = len(N3_SW["Stage"])
    N23_SW_Count = N2_SW_Count+N3_SW_Count

    # Divide to get densities
    Spindle_NREM2_Density.append(N2_Spindle_Count / N2_Count)
    try: # in case there are no n3 epochs
        Spindle_NREM3_Density.append(N3_Spindle_Count / N3_Count)
    except:
        Spindle_NREM3_Density.append(np.nan)
    Spindle_NREM23_Density.append(N23_Spindle_Count / N23_Count)

    SW_NREM2_Density.append(N2_SW_Count / N2_Count)
    try:
        SW_NREM3_Density.append(N3_SW_Count / N3_Count)
    except:
        SW_NREM3_Density.append(np.nan)
    SW_NREM23_Density.append(N23_SW_Count / N23_Count)


    # Record the ID
    IDs.append(ID)
# except Exception as e:
#     print(str(e))
#     print("PROBLEM PROBLEM PROBLEM ***** : ID = %s" % ID)
#     error_file = '%s_%s.txt' % (ID, 'ErrorMSG')
#     error_path = error_dir / error_file
#     with open(error_path, 'w') as file:
#         file.write(str(e))
    
    
    
    
    
"""
Final Table Creation and Saving
"""
Final_Table = pd.DataFrame()

# Add ID
Final_Table["EDF_ID"] = IDs
Final_Table["Age"] = Age
Final_Table["Sex"] = Sex

"""
Slow and Fast Spindles Combined
"""
# Slow and Fast n2n3 Spindle Data
Final_Table["mean_Spindle_RelPower_NREM_All"] = mean_Spindle_RelPower_NREM_All
Final_Table["mean_Spindle_Amplitude_NREM_All"] = mean_Spindle_Amplitude_NREM_All
Final_Table["mean_Spindle_Frequency_NREM_All"] = mean_Spindle_Frequency_NREM_All
Final_Table["mean_Spindle_Duration_NREM_All"] = mean_Spindle_Duration_NREM_All


Final_Table["std_Spindle_RelPower_NREM_All"] = std_Spindle_RelPower_NREM_All
Final_Table["std_Spindle_Amplitude_NREM_All"] = std_Spindle_Amplitude_NREM_All
Final_Table["std_Spindle_Frequency_NREM_All"] = std_Spindle_Frequency_NREM_All
Final_Table["std_Spindle_Duration_NREM_All"] = std_Spindle_Duration_NREM_All

# Slow and Fast n2 Spindle Data
Final_Table["mean_Spindle_Duration_N2_All"] = mean_Spindle_Duration_N2_All
Final_Table["mean_Spindle_Amplitude_N2_All"] = mean_Spindle_Amplitude_N2_All
Final_Table["mean_Spindle_RelPower_N2_All"] = mean_Spindle_RelPower_N2_All
Final_Table["mean_Spindle_Frequency_N2_All"] = mean_Spindle_Frequency_N2_All

Final_Table["std_Spindle_Duration_N2_All"] = std_Spindle_Duration_N2_All
Final_Table["std_Spindle_Amplitude_N2_All"] = std_Spindle_Amplitude_N2_All
Final_Table["std_Spindle_RelPower_N2_All"] = std_Spindle_RelPower_N2_All
Final_Table["std_Spindle_Frequency_N2_All"] = std_Spindle_Frequency_N2_All

# Slow and Fast n3 Spindle Data
Final_Table["mean_Spindle_Duration_N3_All"] = mean_Spindle_Duration_N3_All
Final_Table["mean_Spindle_Amplitude_N3_All"] = mean_Spindle_Amplitude_N3_All
Final_Table["mean_Spindle_RelPower_N3_All"] = mean_Spindle_RelPower_N3_All
Final_Table["mean_Spindle_Frequency_N3_All"] = mean_Spindle_Frequency_N3_All

Final_Table["std_Spindle_Duration_N3_All"] = std_Spindle_Duration_N3_All
Final_Table["std_Spindle_Amplitude_N3_All"] = std_Spindle_Amplitude_N3_All
Final_Table["std_Spindle_RelPower_N3_All"] = std_Spindle_RelPower_N3_All
Final_Table["std_Spindle_Frequency_N3_All"] = std_Spindle_Frequency_N3_All

"""
Slow Spindles
"""
# Slow n2n3 Spindle Data
Final_Table["mean_Slow_Spindle_RelPower_NREM_All"] = mean_Slow_Spindle_RelPower_NREM_All
Final_Table["mean_Slow_Spindle_Amplitude_NREM_All"] = mean_Slow_Spindle_Amplitude_NREM_All
Final_Table["mean_Slow_Spindle_Frequency_NREM_All"] = mean_Slow_Spindle_Frequency_NREM_All
Final_Table["mean_Slow_Spindle_Duration_NREM_All"] = mean_Slow_Spindle_Duration_NREM_All

Final_Table["std_Slow_Spindle_RelPower_NREM_All"] = std_Slow_Spindle_RelPower_NREM_All
Final_Table["std_Slow_Spindle_Amplitude_NREM_All"] = std_Slow_Spindle_Amplitude_NREM_All
Final_Table["std_Slow_Spindle_Frequency_NREM_All"] = std_Slow_Spindle_Frequency_NREM_All
Final_Table["std_Slow_Spindle_Duration_NREM_All"] = std_Slow_Spindle_Duration_NREM_All

# Slow n2 Spindle Data
Final_Table["mean_Slow_Spindle_Duration_N2_All"] = mean_Slow_Spindle_Duration_N2_All
Final_Table["mean_Slow_Spindle_Amplitude_N2_All"] = mean_Slow_Spindle_Amplitude_N2_All
Final_Table["mean_Slow_Spindle_RelPower_N2_All"] = mean_Slow_Spindle_RelPower_N2_All
Final_Table["mean_Slow_Spindle_Frequency_N2_All"] = mean_Slow_Spindle_Frequency_N2_All

Final_Table["std_Slow_Spindle_Duration_N2_All"] = std_Slow_Spindle_Duration_N2_All
Final_Table["std_Slow_Spindle_Amplitude_N2_All"] = std_Slow_Spindle_Amplitude_N2_All
Final_Table["std_Slow_Spindle_RelPower_N2_All"] = std_Slow_Spindle_RelPower_N2_All
Final_Table["std_Slow_Spindle_Frequency_N2_All"] = std_Slow_Spindle_Frequency_N2_All

# Slow n3 Spindle Data
Final_Table["mean_Slow_Spindle_Duration_N3_All"] = mean_Slow_Spindle_Duration_N3_All
Final_Table["mean_Slow_Spindle_Amplitude_N3_All"] = mean_Slow_Spindle_Amplitude_N3_All
Final_Table["mean_Slow_Spindle_RelPower_N3_All"] = mean_Slow_Spindle_RelPower_N3_All
Final_Table["mean_Slow_Spindle_Frequency_N3_All"] = mean_Slow_Spindle_Frequency_N3_All

Final_Table["std__Slow_Spindle_Duration_N3_All"] = std_Slow_Spindle_Duration_N3_All
Final_Table["std__Slow_Spindle_Amplitude_N3_All"] = std_Slow_Spindle_Amplitude_N3_All
Final_Table["std__Slow_Spindle_RelPower_N3_All"] = std_Slow_Spindle_RelPower_N3_All
Final_Table["std__Slow_Spindle_Frequency_N3_All"] = std_Slow_Spindle_Frequency_N3_All

"""
Fats Spindles
"""
Final_Table["mean_Fast_Spindle_RelPower_NREM_All"] = mean_Fast_Spindle_RelPower_NREM_All
Final_Table["mean_Fast_Spindle_Amplitude_NREM_All"] = mean_Fast_Spindle_Amplitude_NREM_All
Final_Table["mean_Fast_Spindle_Frequency_NREM_All"] = mean_Fast_Spindle_Frequency_NREM_All
Final_Table["mean_Fast_Spindle_Duration_NREM_All"] = mean_Fast_Spindle_Duration_NREM_All

Final_Table["std_Fast_Spindle_RelPower_NREM_All"] = std_Fast_Spindle_RelPower_NREM_All
Final_Table["std_Fast_Spindle_Amplitude_NREM_All"] = std_Fast_Spindle_Amplitude_NREM_All
Final_Table["std_Fast_Spindle_Frequency_NREM_All"] = std_Fast_Spindle_Frequency_NREM_All
Final_Table["std_Fast_Spindle_Duration_NREM_All"] = std_Fast_Spindle_Duration_NREM_All

# Slow n2 Spindle Data
Final_Table["mean_Fast_Spindle_Duration_N2_All"] = mean_Fast_Spindle_Duration_N2_All
Final_Table["mean_Fast_Spindle_Amplitude_N2_All"] = mean_Fast_Spindle_Amplitude_N2_All
Final_Table["mean_Fast_Spindle_RelPower_N2_All"] = mean_Fast_Spindle_RelPower_N2_All
Final_Table["mean_Fast_Spindle_Frequency_N2_All"] = mean_Fast_Spindle_Frequency_N2_All

Final_Table["std_Fast_Spindle_Duration_N2_All"] = std_Fast_Spindle_Duration_N2_All
Final_Table["std_Fast_Spindle_Amplitude_N2_All"] = std_Fast_Spindle_Amplitude_N2_All
Final_Table["std_Fast_Spindle_RelPower_N2_All"] = std_Fast_Spindle_RelPower_N2_All
Final_Table["std_Fast_Spindle_Frequency_N2_All"] = std_Fast_Spindle_Frequency_N2_All

# Slow n3 Spindle Data
Final_Table["mean_Fast_Spindle_Duration_N3_All"] = mean_Fast_Spindle_Duration_N3_All
Final_Table["mean_Fast_Spindle_Amplitude_N3_All"] = mean_Fast_Spindle_Amplitude_N3_All
Final_Table["mean_Fast_Spindle_RelPower_N3_All"] = mean_Fast_Spindle_RelPower_N3_All
Final_Table["mean_Fast_Spindle_Frequency_N3_All"] = mean_Fast_Spindle_Frequency_N3_All

Final_Table["std__FastSpindle_Duration_N3_All"] = std_Fast_Spindle_Duration_N3_All
Final_Table["std__FastSpindle_Amplitude_N3_All"] = std_Fast_Spindle_Amplitude_N3_All
Final_Table["std__FastSpindle_RelPower_N3_All"] = std_Fast_Spindle_RelPower_N3_All
Final_Table["std__FastSpindle_Frequency_N3_All"] = std_Fast_Spindle_Frequency_N3_All

"""
Slow wave mean additions
"""
Final_Table["SW Duration"] = sw_Mean_Duration
Final_Table["SW Neg Peak"] = sw_Mean_ValNegPeak
Final_Table["SW Pos Peak"] = sw_Mean_ValPosPeak
Final_Table["SW PTP"] = sw_Mean_PTP
Final_Table["SW Slope"] = sw_Mean_Slope
Final_Table["SW Freq"] = sw_Mean_Frequency
Final_Table["SW Sigma Peak"] = sw_Mean_SigmaPeak
Final_Table["SW Sigma Peak Phase"] = sw_Mean_PhaseAtSigmaPeak
Final_Table["SW ndPAC"] = sw_Mean_ndPAC

Final_Table["SW Duration std"] = sw_std_Duration
Final_Table["SW Neg Peak std"] = sw_std_ValNegPeak
Final_Table["SW Pos Peak std"] = sw_std_ValPosPeak
Final_Table["SW PTP std"] = sw_std_PTP
Final_Table["SW Slope std"] = sw_std_Slope
Final_Table["SW Freq std"] = sw_std_Frequency
Final_Table["SW Sigma Peak std"] = sw_std_SigmaPeak
Final_Table["SW Sigma Peak Phase std"] = sw_std_PhaseAtSigmaPeak
Final_Table["SW ndPAC std"] = sw_std_ndPAC


"""
Complete Table Data
"""
Final_Table["AHINonREM"] = AHINonREM
Final_Table["AHIOverall"] = AHIOverall
# Final_Table["EDF_ID"] = EDF_ID
# Final_Table["Age"] = Age
# Final_Table["Gender"] = Gender
Final_Table["PulseRateMean"] = PulseRateMean
Final_Table["PulseRateStDev"] = PulseRateStDev
Final_Table["PulseRateMax"] = PulseRateMax
Final_Table["PulseRateMin"] = PulseRateMin
Final_Table["HypopneaOverallIndex"] = HypopneaOverallIndex
Final_Table["ApneaOverallIndex"] = ApneaOverallIndex
Final_Table["RDIOverall"] = RDIOverall
Final_Table["RDINonREM"] = RDINonREM
Final_Table["ODI4Overall"] = ODI4Overall
Final_Table["ODI3Overall"] = ODI3Overall
Final_Table["SpO2Mean"] = SpO2Mean
Final_Table["SpO2SD"] = SpO2SD
Final_Table["SpO2Min"] = SpO2Min
Final_Table["SpO2Max"] = SpO2Max
Final_Table["sBMI"] = sBMI

"""
Density Table Data
"""
Final_Table["NREM2_Spindle_Density"] = Spindle_NREM2_Density
Final_Table["NREM3_Spindle_Density"] = Spindle_NREM3_Density
Final_Table["NREM23_Spindle_Density"] = Spindle_NREM23_Density

Final_Table["NREM2_SW_Density"] = SW_NREM2_Density
Final_Table["NREM3_SW_Density"] = SW_NREM3_Density
Final_Table["NREM23_SW_Density"] = SW_NREM23_Density

"""
Append the Cognitive data to the final table
"""



# # Extract the unique EDF_ID values from dataframe1
# edf_ids = Final_Table['EDF_ID'].unique()

# # Filter dataframe2 based on the EDF_ID values from dataframe1
# complete_table = complete_table[complete_table['EDF_ID'].isin(edf_ids)]
# complete_table = complete_table[complete_table['Include_In_Final_Set'] == 1]


print(len(Final_Table['EDF_ID']))
print("Data type of 'EDF_ID' in df1:", Final_Table['EDF_ID'].dtype)

print("***")
print(len(complete_table['EDF_ID']))
print("Data type of 'EDF_ID' in df2:", complete_table['EDF_ID'].dtype)


#  Final_Table = Final_Table.merge(complete_table, on='EDF_ID')

# Export the table
print("Saving Features...")
Final_Table.to_excel("Final_Table_For_Stats.xlsx")
Final_Table.to_csv("Final_Table_For_Stats.csv")
#append(average_frequency = spindle_df.loc[spindle_df['Frequency'] >= 12.5, 'Frequency'].mean())

print("***************************************")
print(count)