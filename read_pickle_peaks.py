import pickle
import pathlib
import pandas as pd
import openpyxl

# Data dir for smoothed data
data_path = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_5_2Data/Peaks/peaks.pkl")
save_path = pathlib.Path("Z:/ResearchHome/ClusterHome/asanch24/APNEA/Block2_5_2Data/Peaks/magnitude.xlsx")

with open(data_path, 'rb') as f:
    """
    1) Load pickle data dictionary smoothed
    """

    print("Importing Data Dictionary...")
    peaks = pickle.load(f)

    # Convert to dataframe
    df = pd.DataFrame(data=peaks, index=[1])
    print("Pickle converted to Dataframe...")

    # Convert to excel
    df.to_excel(save_path, index=False)
    print("Dictionary converted to excel...")
