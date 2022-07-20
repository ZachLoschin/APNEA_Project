import pathlib
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne

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

x = list(range(1,70))
plt.plot(x, psgFirstNights["NREM2Time"], color="blue", label="PSG Classifier")
plt.plot(x, ourDF["NREM2_Time_Night1"], color="red", label="Our Classifier")
plt.title("NREM2 Classification in Hours per Patient Night 1")
plt.legend()
plt.show()
plt.clf()

plt.scatter(psgFirstNights["NREM2Time"], ourDF["NREM2_Time_Night1"])
plt.title("NREM2 Night1")
plt.xlabel("PSG Classification")
plt.ylabel("Our Classification")
plt.show()

