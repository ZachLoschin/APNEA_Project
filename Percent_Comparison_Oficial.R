# Zachary Loschinskey
# St. Jude Children's Research Hospital
# Department of Diagnostic Imaging, Ranga Group
# 7/20/2022

# Creating line graphs of our detected sleep percentages vs the sleep reports

# Import library to read Excel files
library("readxl")

# Define data path
ourDataPath = "C:\\Users\\zloschin\\Percent_Comparison\\StatePercents.xlsx"

# Define data path
psgDataPath = "C:\\Users\\zloschin\\Percent_Comparison\\CompleteTable2.xlsx"

# Import the data
ourData <- read_excel(ourDataPath)
psgData <- read_excel(psgDataPath)

# Convert to data frame
ourDF <- as.data.frame(ourData)
psgDF <- as.data.frame(psgData)

# Separate PSG data into first and second nights
psgFirstNights = psgDF[psgDF$Night == 1]
psgSecondNights = psgDF[psgDF$Night == 2]


ourSecondNights = ourDF[ourDF$Wake_Time_Night2 == 1]

