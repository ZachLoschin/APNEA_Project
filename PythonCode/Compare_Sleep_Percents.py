"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Apnea Project

Description: Extracts average percent in sleep state from each night for each patient in the sleep reports.
Only does this if the sleep report SJID matches one we have our own percent sleep state data for.
"""

import pandas as pd
import numpy as np
import pathlib
import openpyxl

# Path definitions
ourDataPath = pathlib.Path("Z:\\ResearchHome\\ClusterHome\\zloschin\\Spindle_Percent_Data\\Percentage_Data.xlsx")
sleepRepPath = pathlib.Path("Z:\\ResearchHome\\ClusterHome\\zloschin\\Spindle_Percent_Data\\Sleep_Reports.xlsx")
savePath = pathlib.Path("Z:\\ResearchHome\\ClusterHome\\zloschin\\Spindle_Percent_Data\\Percent_Data_Combined.xlsx")

# Read in each xlsx to pd dataframe
ourDF = pd.read_excel(ourDataPath)
reportDF = pd.read_excel(sleepRepPath)

# Make ourIDs into array for searching
ourIDs = np.array(ourDF["SJID"])

# Make fields in ourDF for adding rep times
ourDF["Rep_W"] = np.zeros(len(ourDF["SJID"]))
ourDF["Rep_R"] = np.zeros(len(ourDF["SJID"]))
ourDF["Rep_N1"] = np.zeros(len(ourDF["SJID"]))
ourDF["Rep_N2"] = np.zeros(len(ourDF["SJID"]))
ourDF["Rep_N3"] = np.zeros(len(ourDF["SJID"]))

# Create output dataframe
outDF = pd.DataFrame()


# Find IDs that are in both files
for index, row in reportDF.iterrows():

    # Format the ID properly
    ID = float(row["SJ ID"].split(".")[0][3:])

    # Check if ID is in our DF, if so
    if ID in ourIDs:
        # Get index of ID in ourDF
        ourIndex = int(np.where(ourIDs == ID)[0])

        # Calculate parameters
        w_night1 = float(row["Wake Night 1"].split("%")[0]) / 100
        w_night2 = float(row["Wake Night 2"].split("%")[0]) / 100
        w = (w_night1 + w_night2) / 2

        r_night1 = float(row["REM Night 1"].split("%")[0]) / 100
        r_night2 = float(row["REM Night 2"].split("%")[0]) / 100
        r = (r_night1 + r_night2) / 2

        N1_night1 = float(row["Stage N1 Night 1"].split("%")[0]) / 100
        N1_night2 = float(row["Stage N1 Night 1"].split("%")[0]) / 100
        N1 = (N1_night1 + N1_night2) / 2

        N2_night1 = float(row["Stage N2 Night 1"].split("%")[0]) / 100
        N2_night2 = float(row["Stage N2 Night 1"].split("%")[0]) / 100
        N2 = (N2_night1 + N2_night2) / 2

        N3_night1 = float(row["Stage N3 Night 1"].split("%")[0]) / 100
        N3_night2 = float(row["Stage N3 Night 1"].split("%")[0]) / 100
        N3 = (N3_night1 + N3_night2) / 2

        # Add these parameters to ouDF
        ourDF["Rep_W"][ourIndex] = w
        ourDF["Rep_R"][ourIndex] = r
        ourDF["Rep_N1"][ourIndex] = N1
        ourDF["Rep_N2"][ourIndex] = N2
        ourDF["Rep_N3"][ourIndex] = N3

# Save our data
ourDF.to_excel(savePath)
