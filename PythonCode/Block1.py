"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
6 June 2022
"""


"""
Block Layout:
    1) Library imports
    1.1) Create directories for storing images
    Per patient loop starts:
        2) Raw data import
        3) Creation of our data dictionary
        4) Calculate hypnograms and save to file
            - Includes appending hypno_enum to data {dict}
        5) Calculate time frequency plots and save to file
        6) Save data dictionary to JSON File
"""

"""
1) Library imports
"""

import mne
import My_Funcs as my
import matplotlib.pyplot as plt
import yasa
import pickle
import pathlib

"""
1.1) Create directories for storing images and dictionaries
"""
# Create folders for storing images
hypno_dir = pathlib.Path("Hypnograms/")
hypno_dir.mkdir(parents=True, exist_ok=True)

spectro_dir = pathlib.Path("Spectrograms/")
spectro_dir.mkdir(parents=True, exist_ok=True)

data_dir = pathlib.Path("Data_Dict/")
data_dir.mkdir(parents=True, exist_ok=True)

error_dir = pathlib.Path("Error_Storage/")
error_dir.mkdir(parents=True, exist_ok=True)

# Main loop
with open('files_list.txt', 'r') as a_file:
    print('File Opened')
    for filename in a_file:
        try:
            """
            2) Raw data import
            """
            rawImport = mne.io.read_raw_edf(filename.strip(), preload=True)

            """
            3) Creation of our data dictionary
            """
            # Create epoch vector
            epochVec = my.create_epochs(rawImport["EEG"][0][0], rawImport.info["sfreq"], 30)

            # Create epoch time vector
            epochTimeVec = my.create_epochs(rawImport["EEG"][1], rawImport.info["sfreq"], 30)

            # Create Dictionary for organization
            data = my.create_dict(rawImport["EEG"][0][0], rawImport.info["sfreq"], rawImport["EEG"][1], epochVec,
                                  epochTimeVec)

            """
            4) Calculate hypnograms and save to file
            """

            # Create Sleep Stages
            sls = yasa.SleepStaging(rawImport, eeg_name="EEG")
            sf = rawImport.info["sfreq"]

            # Create Hypno Object
            hypno = sls.predict()

            # Convert hypno to hypno_enum
            hypno_enum = my.hypno_to_plot_art(hypno)

            # Add hypno_enum to the data dictionary
            data["HypnoEnum"] = hypno_enum

            # Create hypnograms
            plt.plot()
            plt.tight_layout()
            plt.yticks([0, 1, 2, 3, 4], ["N3", "N2", "N1", "R", "WAKE"])
            plt.xlabel("Epochs (30s)")
            plt.title('Hypnogram: %s' % filename.strip())
            plt.plot(hypno_enum)

            # Save to output file
            hypno_file = '%s_%s.png' % (filename.strip(), 'Hypnogram')
            hypno_path = hypno_dir / hypno_file
            plt.savefig(hypno_path, bbox_inches="tight")

            # Clear figure window
            plt.clf()

            """
            5) Calculate time frequency plots and save to file
            """

            # Plot spectrogram
            plt.plot()
            plt.tight_layout()
            yasa.plot_spectrogram(rawImport["EEG"][0][0], 256, hypno=None)
            plt.title('Spectrogram: %s' % filename.strip())

            # Save to output file
            spectro_file = '%s_%s.png' % (filename.strip(), 'Spectrogram')
            spectro_path = spectro_dir / spectro_file
            plt.savefig(spectro_path, bbox_inches="tight")

            # Clear figure window
            plt.clf()

            """
            6) Save data dictionary as pickle to omit later mne data loading
            """

            data_file = '%s_%s.pkl' % (filename.strip(), 'Dictionary')
            data_path = data_dir / data_file
            with open(data_path, 'wb+') as f:
                pickle.dump(data, f)

        except:
            error_file = '%s_%s.txt' % (filename.strip(), 'ErrorMSG')
            error_path = error_dir / error_file
            with open(error_path, 'w') as e:
                e.write('Error running %s\n' % filename.strip())
