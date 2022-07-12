import pandas as pd
import numpy as np
import pathlib


"""
Define data directories
"""

"""
This script will read a folder that contains folders. In these subfolders, there are many excel files in each subfolder,
one for each patient's spindle data. It then averages each of these and saves the average frequency for each patient
into a subgroup based excel file.

"""

# This folder holds the folders which hold patient Excel files
folder_holder = pathlib.Path("Z:\\ResearchHome\\ClusterHome\\zloschin\\Spind_Data_Case_Controls")

dict_dir = pathlib.Path("Z:\\ResearchHome\\ClusterHome\\zloschin\\")


# Loop through subgroup folders
for folder in folder_holder.glob('*'):

    # Data frame for holding final data
    Final_Data = pd.DataFrame()

    print(folder)
    # Define the field name for permanent storage df
    field = str(folder).split('\\')[-1]
    print(field)

    # Initialize subgroup wide storage
    subgroupStorage = []
    count = 0
    # In each subgroup folder loop through Excel files
    try:
        for file in folder.glob('*'):
            print(file)
            count = count + 1
            print(count)
            # Save excel file to a tempDF
            tempDF = pd.read_excel(file)

            # Initialize storage vec
            tempFreqVec = []

            # Go through tempDF and return the mean spindle frequency of states N2 N3
            for idx, row in tempDF.iterrows():
                state = row["State"]

                if state == 1 or state == 0:
                    # Add the frequency to tempFreqVec
                    tempFreqVec.append(row["Frequency"])

            # After one patient data, append the mean of tempFreqVec to the permanent storage vec
            print("Save patient to subgroup storage")
            subgroupStorage.append(np.mean(tempFreqVec))
    except:
        continue

    # After each subgroup, save the subgroupStorage to the final data frame under the proper field name
    print("Save subgroup to final storage")
    Final_Data[field] = subgroupStorage

    dict_file = '%s.xlsx' % field
    dict_path = dict_dir / dict_file

    # After all subgroups have been added save the excel file
    Final_Data.to_excel(dict_path)

