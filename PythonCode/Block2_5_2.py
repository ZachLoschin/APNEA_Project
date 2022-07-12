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
    import libraries
    
    1) import data
    2) Create new dict key for NREM only
    3) .pop all ! NREM epochs and concat back to continuous data
    4) take PSD of this and plot
    5) IRASA
    6) Plot aperiodic
    7) Plot oscillatory
"""

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

# Create dir for these folders
block2_5_2dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_5_2Data/")
# block2_5_2dir.mkdir(parents=True, exist_ok=True)

# Create dir for raw psd
NREM_psd_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_5_2Data/PSD_NREM_duplicate/")
#NREM_psd_dir.mkdir(parents=True, exist_ok=True)

dict_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_5_2Data/Peaks_Real/")
#dict_dir.mkdir(parents=True, exist_ok=True)

oscillatory_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_5_2Data/IRASA_Osc_Data_duplicate")
#oscillatory_dir.mkdir(parents=True, exist_ok=True)

# Data dir for smoothed data
data_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_Data/Data_Dict_Smoothed/")

aperiodic_dir = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_5_2Data/IRASA_Ap_Data_duplicate")
#aperiodic_dir.mkdir(parents=True, exist_ok=True)

# Load the data files
files = pathlib.Path(data_dir).glob('*')

# Blacnk dictionary to hold predicted peaks
peaks = {}

# try:
for file in files:
    with open(file, 'rb') as f:

        """
        1) Load pickle data dictionary smoothed
        """

        print("Importing Data Dictionary")
        data = pickle.load(f)
        print(data.keys())

        split_array = str(file).split('\\')
        name = split_array[-1]
        name = name.split('.')[0]
        print(name)
        ID = my.get_ID(file)
        print(ID)

        """
        2) Create new dict for NREM
        """

        data["NREM_EEG_Epochs"] = my.create_epochs(data["EEG_ArtZero"], data["fs"], 30)
        print(len(data["NREM_EEG_Epochs"]))
        """
        3) .pop all !NREM epochs
        """
        print(len(data["HypnoEnum"]))
        data["NREM_EEG"] = []

        for i in range(len(data["NREM_EEG_Epochs"])):
            if data["HypnoEnum"][i] == 0 or data["HypnoEnum"][i] == 1 or data["HypnoEnum"][i] == 2:  # If its w or rem
                data["NREM_EEG"].append(data["NREM_EEG_Epochs"][i])

        data["NREM_EEG"] = np.concatenate(data["NREM_EEG"])

        """
        4) take PSD of this and plot
        """
        # Plot and save .png
        win = int(4 * data["fs"])

        freqs, psd = scipy.signal.welch(data["NREM_EEG"], data["fs"], nperseg=win)

        print("Plotting PSD")
        plt.clf()
        plt.plot(freqs, psd, 'k', lw=2)
        plt.fill_between(freqs, psd, cmap='Spectral')
        plt.xlim(1, 30)
        plt.yscale('log')
        sns.despine()
        plt.title('NREM Art=0 PSD %s' % ID)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('PSD Log($uV^2$/Hz)')
        # plt.show()

        # Save average psd to folder
        NREM_psd_file = '%s_%s.png' % (ID, 'NREM_No_Art_PSD')
        psd_path = NREM_psd_dir / NREM_psd_file

        plt.savefig(psd_path, bbox_inches="tight")
        plt.clf()
        """
        5) IRASA
        """

        print("IRASA RUNNING")
        raw_freqs, raw_psd_aperiodic, raw_psd_osc = yasa.irasa(data["NREM_EEG"], data["fs"], band=(8, 14),
                                                               win_sec=4, return_fit=False)
        print("raw ocsillatory data")
        print(raw_psd_osc[0])

        print("Plotting Aperiodic")
        # Plot the aperiodic component
        plt.plot(raw_freqs, raw_psd_aperiodic[0], 'b', lw=3)
        plt.xlim(1, 30)
        plt.yscale('log')
        sns.despine()
        plt.title("NREM Art=0 Aperiodic Component: %s" % ID)
        plt.xlabel("Frequency (HZ)")
        plt.ylabel("PSD log($uV^2$/Hz)")
        #plt.show()

        # Save the aperiodic graph
        aperiodic_file = '%s_%s.png' % (ID, 'NREM_Aperiodic')
        aperiodic_path = aperiodic_dir / aperiodic_file

        print("Saving Aperiodic")
        plt.savefig(aperiodic_path, bbox_inches="tight")

        plt.clf()
        #
        # print(raw_freqs)
        #
        # print("Plotting oscillatory")
        # # Plot the oscillatory component
        # plt.plot(raw_freqs, (raw_psd_osc[0]), 'b', lw=2)
        # plt.xlim(8, 18)
        # sns.despine()
        # plt.title("NREM Art=0 Oscillatory Component: %s" % ID)
        # plt.xlabel("Frequency (HZ)")
        # plt.ylabel("PSD log($uv^2$/Hz)")
        #
        # plt.grid(axis='x', b=True, which='major', color='b', linestyle='-')
        # plt.grid(axis='x', b=True, which='minor', color='b', linestyle='--')
        # #plt.show()
        # plt.clf()

        #
        # # Smooth using root mean squared
        # windows = []
        # for i in range(len(raw_psd_osc - 4)):
        #     windows.append(raw_psd_osc[i])
        #     windows.append(raw_psd_osc[i+1])
        #     windows.append(raw_psd_osc[i+2])
        #     windows.append(raw_psd_osc[i+3])
        #     windows.append(raw_psd_osc[i+4])
        #
        #
        #
        # print("FOR THING PRINT")
        # for thing in windows:
        #     print(thing)

        proc = savgol_filter(raw_psd_osc[0], 3, 2)
        max_val = max(proc)
        ax_index = np.where(proc == max_val)
        peaks[ID] = raw_freqs[ax_index]  # Hopefully there are no cases where the max value occurs twice

        print("Plotting oscillatory")
        # Plot the oscillatory component
        plt.plot(raw_freqs, proc, 'b', lw=2)
        plt.xlim(8, 13)
        sns.despine()
        plt.title("NREM Art=0 Oscillatory Component Savgol Filtered: %s" % ID)
        plt.xlabel("Frequency (HZ)")
        plt.ylabel("PSD log($uv^2$/Hz)")

        plt.grid(axis='x', b=True, which='major', color='b', linestyle='-')
        plt.grid(axis='x', b=True, which='minor', color='b', linestyle='--')
        # Save the oscillatory graphs
        osc_file = '%s_%s.png' % (ID, 'NREM_Oscillatory_Savgol')
        osc_path = oscillatory_dir / osc_file

        plt.savefig(osc_path, bbox_inches="tight")
        # plt.show()
        plt.clf()

dict_file = 'peaks.pkl'
dict_path = dict_dir / dict_file
with open(dict_path, 'wb+') as f:
    pickle.dump(peaks, f)
