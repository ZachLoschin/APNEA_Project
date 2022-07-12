import pickle
import pathlib
import My_Funcs as my
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import seaborn as sns
import pandas as pd
import yasa
from scipy.signal import savgol_filter

data_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_Data/Data_Dict_Smoothed_Test/")

# Load the data files
files = pathlib.Path(data_dir).glob('*')

for file in files:
    with open(file, 'rb') as f:
        print("Importing Data Dictionary")
        data = pickle.load(f)
        print(data.keys())

        split_array = str(file).split('\\')
        name = split_array[-1]
        name = name.split('.')[0]
        print(name)
        ID = my.get_ID(file)
        print(ID)

        for i in range(len(data["EEG_ArtZero"])):
            if abs(data["EEG_ArtZero"][i]) >= 100:
                data["EEG_ArtZero"][i] = 0
        plt.clf()
        plt.plot(data["EEG_ArtZero"])
        plt.ylim(-200, 200)
        plt.show()