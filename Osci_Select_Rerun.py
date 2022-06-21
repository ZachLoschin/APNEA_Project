"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
9 June 2022
"""


"""
Block Layout:
    Prep: Library Import
    1) Import excel data to pd dataframe
    Per patient loop:
        2) IRASA
        3) Plot oscillatory component (5-18) range and save plot
"""

"""
Library Import
"""

import pickle
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import seaborn as sns
import pandas as pd
import yasa
import My_Funcs as my

"""
Define directories for reading data
and saving new graphs
"""

# Define the folder holding the pickle files
data_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block1_Data/Data_Dict")

# Define the folder holding the oscillatory graphs
oscillatory_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_Data/Oscillatory_Graphs_Extd_Range/")
oscillatory_dir.mkdir(parents=True, exist_ok=True)

# Define the file names
files = pathlib.Path(data_dir).glob('*')

# Load the Excel file as pd dataframe
df = pd.read_excel(r'Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_Data')
for file in files:
    ID = my.get_ID(file)
    print(ID)





