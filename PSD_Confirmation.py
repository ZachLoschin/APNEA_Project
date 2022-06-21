import mne
import My_Funcs as my
import matplotlib.pyplot as plt
import yasa
import pickle
import pathlib
import scipy.signal


file_dir = pathlib.Path('Z:/ResearchHome/ClusterHome/asanch24/APNEA/APNEA Raw Files/Test_EDF/').glob('*')


for filename in file_dir:

    """
    2) Raw data import
    """
    split_array = str(filename).split('\\')
    name = split_array[-1]

    rawImport = mne.io.read_raw_edf(filename, preload=True)

    my.my_plot(rawImport["EEG"][0][0], rawImport["EEG"][1], "Raw Import Data", 1)

    win = int(4 * rawImport.info["sfreq"])

    freqs, psd = scipy.signal.welch(rawImport["EEG"][0][0], rawImport.info["sfreq"], nperseg=win)

    print("Plotting PSD")
    plt.clf()
    plt.plot(freqs, psd, 'k', lw=2)
    plt.fill_between(freqs, psd, cmap='Spectral')
    plt.xlim(1, 30)
    plt.yscale('log')
    plt.title('Raw Import PSD')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('PSD Log($uV^2$/Hz)')
    plt.show()
