"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
8 June 2022
"""
import yasa
import numpy as np

"""
Block Layout:
    Prep: Import Libraries
    Per Patient Loop:
        1) Load Data Structure
        2) Isolate NREM Epochs without artifacts > 100uV
        3) Take PSD for each epoch
        4) Take IRASA for each epoch
        5) Calculate Average PSD and IRASA and Save Plots as .png and .txt
"""

"""
Prep: Import Libraries
"""

import My_Funcs as my
import pickle
import pathlib
import scipy.signal
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

"""
1) Load Data Structure
"""

# Define the folder holding the pickle files
data_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block1_Data/Subset_For_Testing/")

# Load the data files
files = pathlib.Path(data_dir).glob('*')

for file in files:
    with open(file, 'rb') as f:
        print("Importing Data Dictionary")
        data = pickle.load(f)
        print(data.keys())

        split_array = str(file).split('\\')
        name = split_array[-1]

        """
        2) Isolate NREM Epochs without artifacts > 100uV
        """

        # Add keys to dictionary for only NREM epochs and corresponding time vectors
        data["NREM_Epochs"] = []
        data["NREM_Indeces"] = []

        # Populate new dictionary keys
        threshold = 100  # uV
        """
        THE NREM EPOCH VEC AND INDICES VEC HAS
        BEEN CREATED IN THE BLOCK 1.5 CODE 
        AS OF 8 JUNE 2022
        """

        for i in range(len(data["HypnoEnum"])):
            if data["HypnoEnum"][i] == 0 or data["HypnoEnum"][i] == 1 or data["HypnoEnum"][i] == 2:
                if max(data["EpochVec"][i]) < threshold:
                    data["NREM_Epochs"].append(data["EpochVec"][i])
                    data["NREM_Indeces"].append(i)

        """
        3) Take PSD for each epoch
        """
        # Add psd and freq fields to our dictionary
        data["PSDVec"] = []
        data["freqsVec"] = []

        win = int(4 * data["fs"])

        # Get the psd for each 30 second epoch
        for i in range(len(data["NREM_Epochs"])):
            freqs, psd = scipy.signal.welch(data["NREM_Epochs"][i], data["fs"], nperseg=win)
            data["PSDVec"].append(psd)
            data["freqsVec"].append(freqs)


        # """
        # 4) Take IRASA for each epoch
        # """
        #
        # # Add keys to dictionary for storage
        # data["raw_freqs"] = []
        # data["raw_psd_aperiodic"] = []
        # data["raw_psd_osc"] = []
        #
        # for i in range(len(data["NREM_Epochs"])):
        #     raw_freqs, raw_psd_aperiodic, raw_psd_osc = yasa.irasa(data["NREM_Epochs"][i], data["fs"], band=(9,18), win_sec=3, return_fit=False)
        #     data["raw_freqs"].append(raw_freqs)
        #     data["raw_psd_aperiodic"].append(raw_psd_aperiodic)
        #     data["raw_psd_osc"].append(raw_psd_osc)


        """
        5) Calculate Average PSD and IRASA and Save Plots as .png and .txt
        """

        # Create pd data frame of PSD data
        psd_df = pd.DataFrame(data["PSDVec"])
        ave_psd = np.array(psd_df.mean(axis=0))
        ave_freqs = data["freqsVec"][1]

        plt.plot(ave_freqs, ave_psd, 'k', lw=2)
        plt.fill_between(ave_freqs, ave_psd, cmap='Spectral')
        plt.xlim(1, 30)
        plt.yscale('log')
        sns.despine()
        plt.title('PSD %s' % name)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('PSD Log($uV^2$/Hz)')
        plt.show()
