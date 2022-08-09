from PyPDF2 import PdfFileReader
import pandas as pd
import glob, os
import numpy as np

"""
Zachary Loschinskey
St. Jude Children's Research Hospital
Department of Diagnostic Imaging
Ranga Group
Sleep Apnea Project
28 June 2022
"""

"""
Scrape the sleep reports to get the recording times for each night.
Complete this in order to split the .edf file into night by night recordings.
"""

# Define the path and index
os.chdir(r"C:\Users\asanch24\OneDrive - St. Jude Children's Research Hospital\SleepResearch\APNEA Project\Sleep_reports")
index = np.linspace(1,len(glob.glob("*.pdf")),len(glob.glob("*.pdf")))

count = 0

# Create new datatable for holding data
columns = ['Patient', 'Recording_Time_N1', 'Recording_Time_N2']
NewTable = pd.DataFrame(index=index, columns=columns)

for file in glob.glob("*.pdf"):
    print(file)

    # Get the text from the page
    reader = PdfFileReader(file)
    numberPages = reader.numPages

    # Read the page that has the data we want
    page = reader.pages[2]
    text = page.extractText()

    # Find "Recording Time"
    idx_recTime = text.find("Recording")
    recTimeText = text[idx_recTime:]

    # Find the next h starting at recording time
    h_idx = recTimeText.find("h")
    recTimeN1 = recTimeText[h_idx-3:h_idx+1]
    print(recTimeN1)

    # Find the next h
    recTimeText = text[idx_recTime+18:]
    h_idx = recTimeText.find("h")
    recTimeN2 = recTimeText[h_idx-3:h_idx+1]
    print(recTimeN2)
    print(type(recTimeN2))

    # Append these values to the data table
    NewTable["Recording_Time_N1"][count] = recTimeN1
    NewTable["Recording_Time_N2"][count] = recTimeN2
    NewTable["Patient"][count] = file
    # Increment the count
    count = count+1

print(NewTable)
# Save the Excel table
NewTable.to_excel("Test.xlsx")

