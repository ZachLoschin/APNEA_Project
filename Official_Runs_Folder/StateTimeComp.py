import pathlib
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne


def plot_comparisons(ourline, ourline2, psgline, psgline2, state, filepath):
    # Create line for plotting
    x = list(range(1, len(ourline)+1))
    x2 = list(range(1, len(ourline2) + 1))

    line = list(range(0, len(ourline)+1))

    # Define figure, 2 types of plots, 2 nights
    fig, axs = plt.subplots(2,2)
    plt.subplots_adjust(left=0.1,
                        bottom=0.1,
                        right=0.9,
                        top=0.9,
                        wspace=0.4,
                        hspace=0.4)

    # Plot the night 1 lines
    axs[0, 0].plot(x, ourline, color="blue", label="Our Classifier")
    axs[0, 0].plot(x, psgline, color="red", label="PSG Classifier")
    axs[0, 0].set_title("Night 1 Lines: %s" % state)
    axs[0, 0].legend()

    # Plot the night 1 scatter
    axs[1, 0].scatter(psgline, ourline)
    axs[1, 0].plot(line, line)
    axs[1, 0].set_xlim(0, max(psgline)+0.25)
    axs[1, 0].set_ylim(0, max(ourline)+0.25)
    axs[1, 0].set_title("Night 1 Scatter: %s" % state)

    # Plot the night 2 lines
    axs[0, 1].plot(x2, ourline2, color="blue", label="Our Classifier")
    axs[0, 1].plot(x2, psgline2, color="red", label="PSG Classifier")
    axs[0, 1].set_title("Night 2 Lines: %s" % state)
    axs[0, 1].legend()

    # Plot the night 2 scatter
    axs[1, 1].scatter(psgline2, ourline2)
    axs[1, 1].plot(line, line)
    axs[1, 1].set_xlim(0, max(psgline2)+0.25)
    axs[1, 1].set_ylim(0, max(ourline2)+0.25)
    axs[1, 1].set_title("Night 2 Scatter: %s" % state)

    fig.savefig(filepath)


# Local data folder for our data
ourData = pathlib.Path("C:\\Users\\zloschin\\Percent_Comparison\\StatePercents.xlsx")

# Local data for psg2 data
psgData = pathlib.Path("C:\\Users\\zloschin\\Percent_Comparison\\CompleteTable2.xlsx")

ourDF = pd.read_excel(ourData)
psgDF = pd.read_excel(psgData)
psgDF = psgDF[psgDF['EDF_ID'] != 176]

# Sort both ascending
psgDF = psgDF.sort_values(by="EDF_ID")
ourDF = ourDF.sort_values(by="IDs")

# night counts are backwards
ourSecondNights = ourDF[ourDF["NightsCount"] == 1]

# Separate nights in the psg data
psgFirstNights = psgDF[psgDF['Night'] == 1]
psgSecondNights = psgDF[psgDF['Night'] == 2]

dict_dir = pathlib.Path("State_Comparisons_Fixed/")
wakePath = dict_dir / "Wake_Comparisons.png"
remPath = dict_dir / "REM_Comparisons.png"
nrem1Path = dict_dir / "NREM1_Comparisons.png"
nrem2Path = dict_dir / "NREM2_Comparisons.png"
nrem3Path = dict_dir / "NREM3_Comparisons.png"

# Plot wake
plot_comparisons(ourDF["Wake_Time_Night1"], ourSecondNights["Wake_Time_Night2"], psgFirstNights["WakeTime"],
                 psgSecondNights["WakeTime"], "Wake", wakePath)

# Plot REM
plot_comparisons(ourDF["REM_Time_Night1"], ourSecondNights["REM_Time_Night2"], psgFirstNights["REMTime"],
                 psgSecondNights["REMTime"], "REM", remPath)

# Plot NREM1
plot_comparisons(ourDF["NREM1_Time_Night1"], ourSecondNights["NREM1_Time_Night2"], psgFirstNights["NREM1Time"],
                 psgSecondNights["NREM1Time"], "NREM1", nrem1Path)

# Plot NREM2
plot_comparisons(ourDF["NREM2_Time_Night1"], ourSecondNights["NREM2_Time_Night2"], psgFirstNights["NREM2Time"],
                 psgSecondNights["NREM2Time"], "NREM2", nrem2Path)

# Plot NREM3
plot_comparisons(ourDF["NREM3_Time_Night1"], ourSecondNights["NREM3_Time_Night2"], psgFirstNights["NREM3Time"],
                 psgSecondNights["NREM3Time"], "NREM3", nrem3Path)
