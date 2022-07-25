################################################################################
#
# Zachary Loschinskey
# St. Jude Children's Research Hospital
# Department of Diagnostic Imaging, Ranga Group
# Statistical Analysis for Sleep Apnea Project
# 22 July 2022
#
################################################################################

# This script is for the t test analysis of case vs control and
# OSA vs non-OSA spindle frequency data

# Import needed libraries
library("readxl")

# Function for substringing from right side
substrRight <- function(x, n){
  substr(x, nchar(x)-n+1, nchar(x))
}

# Set up path for plot storage
histpath = "C:\\Users\\zloschin\\Documents\\APNEA_Project\\T_Test_Graphs"


################################################################################
#
# This block imports data for the Cases with OSA, averages each nights intra-
# spindle frequency and duration, then saves to a night dependent vector for
# later t-test analysis
#
################################################################################


# Define list of Cases OSA files
fileListCasesOsa <- list.files(
path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Summer_Analysis\\Cases_OSA",
                            full.names = TRUE,
                            recursive = TRUE)

# Vector to hold the average spindle frequency for night1 of each participant
freqsCasesOsaN1 <- c()

# Vector to hold the average spindle frequency for night2 of each participant
freqsCasesOsaN2 <- c()

# Vector to hold the average spindle duration for night1 of each participant
durationCasesOsaN1 <- c()

# Vector to hold the average spindle duration for night2 of each participant
durationCasesOsaN2 <- c()


# Loop through each .xlsx file in the case OSA group
for(i in 1:length(fileListCasesOsa)){
  # Read in excel
  tempDF <- read_excel(fileListCasesOsa[i])
  
  # Convert to data frame for easy use
  tempDF <- as.data.frame(tempDF)
  
  # Select only N2 (1) and N3 (0) sleep states
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  
  # Select only slow spindles (<=12.5 Hz)
  tempDF4 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  # Extract the mean frequency from the data frame
  meanFreq <- mean(tempDF4$Frequency, na.rn=TRUE)
  
  # Extract the mean duration from the data frame
  meanDuration <- mean(tempDF4$Duration, na.rn=TRUE)
  
  # Find if this is a night one or night 2 Excel file
  night = substrRight(fileListCasesOsa[i], 6)
  night = as.numeric(substr(night, 1, 1))
  
  # Append the mean to the right storage vector depending on the night value
  if(night == 1){
    freqsCasesOsaN1 = append(freqsCasesOsaN1, meanFreq)
    durationCasesOsaN1 = append(durationCasesOsaN1, meanDuration)
  } else{
    freqsCasesOsaN2 = append(freqsCasesOsaN2, meanFreq)
    durationCasesOsaN2 = append(durationCasesOsaN2, meanDuration)
  }
  
  # Visual confirmation the code is running properly
  cat("Night done...")
  
} # End for loop

################################################################################
#
# This block imports data for the Cases nonOSA, averages each nights intra-
# spindle frequency and duration, then saves to a night dependent vector for
# later t-test analysis
#
################################################################################

# Define list of Cases OSA files
fileListCasesNonOsa <- list.files(
  path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Summer_Analysis\\Cases_nonOSA",
  full.names = TRUE,
  recursive = TRUE)

# Vector to hold the average spindle frequency for night1 of each participant
freqsCasesNonOsaN1 <- c()

# Vector to hold the average spindle frequency for night2 of each participant
freqsCasesNonOsaN2 <- c()

# Vector to hold the average spindle duration for night1 of each participant
durationCasesNonOsaN1 <- c()

# Vector to hold the average spindle duration for night2 of each participant
durationCasesNonOsaN2 <- c()


# Loop through each .xlsx file in the case OSA group
for(i in 1:length(fileListCasesNonOsa)){
  # Read in excel
  tempDF <- read_excel(fileListCasesNonOsa[i])
  
  # Convert to data frame for easy use
  tempDF <- as.data.frame(tempDF)
  
  # Select only N2 (1) and N3 (0) sleep states
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  
  # Select only slow spindles (<=12.5 Hz)
  tempDF4 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  # Extract the mean frequency from the data frame
  meanFreq <- mean(tempDF4$Frequency, na.rn=TRUE)
  
  # Extract the mean duration from the data frame
  meanDuration <- mean(tempDF4$Duration, na.rn=TRUE)
  
  # Find if this is a night one or night 2 Excel file
  night = substrRight(fileListCasesNonOsa[i], 6)
  night = as.numeric(substr(night, 1, 1))
  
  # Append the mean to the right storage vector depending on the night value
  if(night == 1){
    freqsCasesNonOsaN1 = append(freqsCasesNonOsaN1, meanFreq)
    durationCasesNonOsaN1 = append(durationCasesNonOsaN1, meanDuration)
  } else{
    freqsCasesNonOsaN2 = append(freqsCasesNonOsaN2, meanFreq)
    durationCasesNonOsaN2 = append(durationCasesNonOsaN2, meanDuration)
  }
  
  # Visual confirmation the code is running properly
  cat("Night done...")
  
} # End for loop

################################################################################
#
# This block imports data for the controls OSA, averages each nights intra-
# spindle frequency and duration, then saves to a night dependent vector for
# later t-test analysis
#
################################################################################

# Define list of Controls OSA files
fileListControlsOsa <- list.files(
  path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Summer_Analysis\\Controls_OSA",
  full.names = TRUE,
  recursive = TRUE)

# Vector to hold the average spindle frequency for night1 of each participant
freqsControlsOsaN1 <- c()

# Vector to hold the average spindle frequency for night2 of each participant
freqsControlsOsaN2 <- c()

# Vector to hold the average spindle duration for night1 of each participant
durationControlsOsaN1 <- c()

# Vector to hold the average spindle duration for night2 of each participant
durationControlsOsaN2 <- c()


# Loop through each .xlsx file in the case OSA group
for(i in 1:length(fileListControlsOsa)){
  # Read in excel
  tempDF <- read_excel(fileListControlsOsa[i])
  
  # Convert to data frame for easy use
  tempDF <- as.data.frame(tempDF)
  
  # Select only N2 (1) and N3 (0) sleep states
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  
  # Select only slow spindles (<=12.5 Hz)
  tempDF4 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  # Extract the mean frequency from the data frame
  meanFreq <- mean(tempDF4$Frequency, na.rn=TRUE)
  
  # Extract the mean duration from the data frame
  meanDuration <- mean(tempDF4$Duration, na.rn=TRUE)
  
  # Find if this is a night one or night 2 Excel file
  night = substrRight(fileListControlsOsa[i], 6)
  night = as.numeric(substr(night, 1, 1))
  
  # Append the mean to the right storage vector depending on the night value
  if(night == 1){
    freqsControlsOsaN1 = append(freqsControlsOsaN1, meanFreq)
    durationControlsOsaN1 = append(durationControlsOsaN1, meanDuration)
  } else{
    freqsControlsOsaN2 = append(freqsControlsOsaN2, meanFreq)
    durationControlsOsaN2 = append(durationControlsOsaN2, meanDuration)
  }
  
  # Visual confirmation the code is running properly
  cat("Night done...")
  
} # End for loop

################################################################################
#
# This block imports data for the controls nonOSA, averages each nights intra-
# spindle frequency and duration, then saves to a night dependent vector for
# later t-test analysis
#
################################################################################

# Define list of control nonOSA files
fileListControlsnonOsa <- list.files(
  path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Summer_Analysis\\Controls_nonOSA",
  full.names = TRUE,
  recursive = TRUE)

# Vector to hold the average spindle frequency for night1 of each participant
freqsControlsnonOsaN1 <- c()

# Vector to hold the average spindle frequency for night2 of each participant
freqsControlsnonOsaN2 <- c()

# Vector to hold the average spindle duration for night1 of each participant
durationControlsnonOsaN1 <- c()

# Vector to hold the average spindle duration for night2 of each participant
durationControlsnonOsaN2 <- c()


# Loop through each .xlsx file in the case OSA group
for(i in 1:length(fileListControlsnonOsa)){
  # Read in excel
  tempDF <- read_excel(fileListControlsnonOsa[i])
  
  # Convert to data frame for easy use
  tempDF <- as.data.frame(tempDF)
  
  # Select only N2 (1) and N3 (0) sleep states
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  
  # Select only slow spindles (<=12.5 Hz)
  tempDF4 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  # Extract the mean frequency from the data frame
  meanFreq <- mean(tempDF4$Frequency, na.rn=TRUE)
  
  # Extract the mean duration from the data frame
  meanDuration <- mean(tempDF4$Duration, na.rn=TRUE)
  
  # Find if this is a night one or night 2 Excel file
  night = substrRight(fileListControlsnonOsa[i], 6)
  night = as.numeric(substr(night, 1, 1))
  
  # Append the mean to the right storage vector depending on the night value
  if(night == 1){
    freqsControlsnonOsaN1 = append(freqsControlsnonOsaN1, meanFreq)
    durationControlsnonOsaN1 = append(durationControlsnonOsaN1, meanDuration)
  } else{
    freqsControlsnonOsaN2 = append(freqsControlsnonOsaN2, meanFreq)
    durationControlsnonOsaN2 = append(durationControlsnonOsaN2, meanDuration)
  }
  
  # Visual confirmation the code is running properly
  cat("Night done...")
  
} # End for loop

################################################################################
#
# This code block completes the T-tests between frequency and duration between
# Cases: OSA and Cases: nonOSA. Then, graphs are generated and displayed in
# the plots window for visual inspection
#
################################################################################

# Night 1 T-Tests
freqsTTestN1 = t.test(freqsCasesOsaN1, freqsCasesNonOsaN1)
durationTTestN1 = t.test(durationCasesOsaN1, durationCasesNonOsaN1)

# Night 2 T-Tests
freqsTTestN2 = t.test(freqsCasesOsaN2, freqsCasesNonOsaN2)
durationTTestN2 = t.test(durationCasesOsaN2, durationCasesNonOsaN2)

# Define plot colors
myBlue <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue25")
myRed <- rgb(255, 0, 0, max = 255, alpha = 50, names = "red25")

# Night 1 graph freqs
# png("C:\\Users\\zloschin\\Documents\\APNEA_Project_New\\Official_Runs_Folder
#     \\Ttest_Histograms\\Cases_OSA_Freqs_Night1.png")
freqValuesOSA = na.omit(freqsCasesOsaN1)
freqValuesnonosa= na.omit(freqsCasesNonOsaN1)
hist(freqValuesOSA, col=myRed, breaks=25, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Frequency Cases Osa Vs Cases NonOSA Comparison Night 1\nT-Test P-val =", 
                  round(freqsTTestN1$p.value, digits=3), 
                  "\n", "DF =", round(freqsTTestN1$parameter, digits=3)))

lines(density(freqValuesOSA), col='red')

hist(freqValuesnonosa, col=myBlue, breaks=25, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Frequency Cases Osa Vs Cases NonOSA Comparison Night 1 \nT-Test P-val =", 
                  round(freqsTTestN1$p.value, digits=3), 
                  "\n", "DF =", round(freqsTTestN1$parameter, digits=3)), add=TRUE)

lines(density(freqValuesnonosa), col='blue')
legend("topleft", c("Cases OSA", "Cases NonOSA"), fill=c("red", "blue"))
# dev.off()



# Night 2 graph freqs
freqValuesOSA = na.omit(freqsCasesOsaN2)
freqValuesnonosa= na.omit(freqsCasesNonOsaN2)
hist(freqValuesOSA, col=myRed, breaks=25, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Frequency Cases Osa Vs Cases NonOSA Comparison Night 2 \nT-Test P-val =", 
                  round(freqsTTestN2$p.value, digits=3), 
                  "\n", "DF =", round(freqsTTestN2$parameter, digits=3)))

lines(density(freqValuesOSA), col='red')

hist(freqValuesnonosa, col=myBlue, breaks=25, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Frequency Cases Osa Vs Cases NonOSA Comparison Night 2 \nT-Test P-val =", 
                  round(freqsTTestN2$p.value, digits=3), 
                  "\n", "DF =", round(freqsTTestN2$parameter, digits=3)), add=TRUE)

lines(density(freqValuesnonosa), col='blue')
legend("topleft", c("Cases OSA", "Cases NonOSA"), fill=c("red", "blue"))



# Night 1 graphs duration
durationValuesOSA = na.omit(durationCasesOsaN1)
durationValuesnonosa= na.omit(durationCasesNonOsaN1)
hist(durationValuesOSA, col=myRed, breaks=25, xlab="Spindle Duration", 
     ylab="Number of Patients",
     ylim=c(0,5),
     main = paste("Spindle Duration Cases Osa Vs Cases NonOSA Comparison Night 1 \nT-Test P-val =", 
                  round(freqsTTestN1$p.value, digits=3), 
                  "\n", "DF =", round(freqsTTestN1$parameter, digits=3)))

lines(density(durationValuesOSA), col='red')

hist(durationValuesnonosa, col=myBlue, breaks=25, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Duration Cases Osa Vs Cases NonOSA Comparison Night 1 \nT-Test P-val =", 
                  round(freqsTTestN1$p.value, digits=3), 
                  "\n", "DF =", round(freqsTTestN1$parameter, digits=3)), add=TRUE)

lines(density(durationValuesnonosa), col='blue')
legend("topleft", c("Cases OSA", "Cases NonOSA"), fill=c("red", "blue"))



# Night 2 graphs duration
durationValuesOSA = na.omit(durationCasesOsaN2)
durationValuesnonosa= na.omit(durationCasesNonOsaN2)
hist(durationValuesOSA, col=myRed, breaks=25, xlab="Spindle Duration", 
     ylab="Number of Patients",
     ylim=c(0,5),
     main = paste("Spindle Duration Cases Osa Vs Cases NonOSA Comparison Night 2 \nT-Test P-val =", 
                  round(freqsTTestN1$p.value, digits=3), 
                  "\n", "DF =", round(freqsTTestN1$parameter, digits=3)))

lines(density(durationValuesOSA), col='red')

hist(durationValuesnonosa, col=myBlue, breaks=25, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     ylim=c(0,5),
     main = paste("Duration Cases Osa Vs Cases NonOSA Comparison Night 2 \nT-Test P-val =", 
                  round(freqsTTestN1$p.value, digits=3), 
                  "\n", "DF =", round(freqsTTestN1$parameter, digits=3)), add=TRUE)

lines(density(durationValuesnonosa), col='blue')
legend("topleft", c("Cases OSA", "Cases NonOSA"), fill=c("red", "blue"))


