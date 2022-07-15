from importlib.resources import files
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yasa
import mne
import scipy

''''
What this code does:
    1. Create directories
    2. Yasa spindle detection
    3. Artifact removal
    4. Filters: band pass filter and beta pass filter
'''

'''
Create directories
'''

# Local data folder for testing
test_dir = pathlib.Path("../Apnea_Local/Data")
test_dir.mkdir()

# Local dict for holding output excel data
dict_dir = pathlib.Path("../Apnea_Local/Excel_Data/")

# Local plot saving directory
dens_dir = pathlib.Path("../Apnea_Local/Plot_Data")
dens_dir.mkdir(parents=True, exist_ok=True)

# Local data for reading in .edf files
data_dir = pathlib.Path("../Apnea_Local/Data")
files = pathlib.Path(data_dir).glob('*')

