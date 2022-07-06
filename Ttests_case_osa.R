# Zachary Loschinskey
# St. Jude Children's Research Hospital
# Department of Diagnostic Imaging, Ranga Group
# statistical Analysis for Sleep Apnea Project
# 1 July 2022

# This script is for the t test analysis of case vs control and
# OSA vs non-OSA spindle frequency data


# Import library to read Excel files
library("readxl")


# Set up path for plot storage
histpath = "C:\\Users\\zloschin\\Documents\\APNEA_Project\\T_Test_Graphs"


# Cases: OSA vs non-OSA comparison


# Define list of files
file_list_osa <- list.files(path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Spind_Data_Cases\\Cases_OSA_Excel_Data",
                             full.names = TRUE,
                             recursive = TRUE)

freqValuesOSA <- c()

for(i in 1:length(file_list_osa)){
  # Read in excel
  tempDF <- read_excel(file_list_osa[i])
  tempDF <- as.data.frame(tempDF)
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  tempDF4 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  freqs <- mean(tempDF4$Frequency, na.rn=TRUE)
  freqValuesOSA = append(freqValuesOSA, freqs)
}

# Define list of files for nonOSA
file_list_nonosa <- list.files(path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Spind_Data_Cases\\Cases_NonOSA_Excel_Data",
                            full.names = TRUE,
                            recursive = TRUE)

freqValuesnonosa <- c()

for(i in 1:length(file_list_nonosa)){
  # Read in excel
  tempDF <- read_excel(file_list_nonosa[i])
  tempDF <- as.data.frame(tempDF)
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  tempDF3 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  freqs <- mean(tempDF3$Frequency, na.rn=TRUE)
  freqValuesnonosa = append(freqValuesnonosa, freqs)
}


testResult = t.test(freqValuesOSA, freqValuesnonosa, var.equal=TRUE )


# Define plot colors
myBlue <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue25")
myRed <- rgb(255, 0, 0, max = 255, alpha = 50, names = "red25")

png("C:\\Users\\zloschin\\Documents\\APNEA_Project\\T_Test_Graphs\\Cases_Osa_vs_nonOSA.png")
freqValuesOSA = na.omit(freqValuesOSA)
freqValuesnonosa= na.omit(freqValuesnonosa)
hist(freqValuesOSA, col=myRed, breaks=20, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Cases: Osa Vs NonOSA Comparison \nT-Test P-val =", 
                  round(testResult$p.value, digits=3), "\nDF =", 
                  testResult$parameter))

lines(density(freqValuesOSA), col='red')

hist(freqValuesnonosa, col=myBlue, breaks=20, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Cases: Osa Vs NonOSA Comparison \nT-Test P-val =", 
                  round(testResult$p.value, digits=3), "\nDF =", 
                  testResult$parameter), add=TRUE)

lines(density(freqValuesnonosa), col='blue')
legend("topright", c("OSA", "NonOSA"), fill=c("red", "blue"))

dev.off()


# Check for case normality
qqnorm(freqValuesOSA, main='Cases: Osa Check for Normality')
qqline(freqValuesOSA)

qqnorm(freqValuesnonosa, main='Cases: NonOSA Check for Normality')
qqline(freqValuesnonosa)



# Controls: OSA vs nonOSA comparison



# Define list of files
file_list_osa <- list.files(path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Spindle_Data_Controls\\Control_OSA_Excel_Data",
                            full.names = TRUE,
                            recursive = TRUE)

freqValuesOSA <- c()

for(i in 1:length(file_list_osa)){
  # Read in excel
  tempDF <- read_excel(file_list_osa[i])
  tempDF <- as.data.frame(tempDF)
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  tempDF4 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  freqs <- mean(tempDF4$Frequency, na.rn=TRUE)
  freqValuesOSA = append(freqValuesOSA, freqs)
}

# Define list of files for nonOSA
file_list_nonosa <- list.files(path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Spindle_Data_Controls\\Control_NonOSA_Excel_Data",
                               full.names = TRUE,
                               recursive = TRUE)

freqValuesnonosa <- c()

for(i in 1:length(file_list_nonosa)){
  # Read in excel
  tempDF <- read_excel(file_list_nonosa[i])
  tempDF <- as.data.frame(tempDF)
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  tempDF3 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  freqs <- mean(tempDF3$Frequency, na.rn=TRUE)
  freqValuesnonosa = append(freqValuesnonosa, freqs)
}


testResult = t.test(freqValuesOSA, freqValuesnonosa, var.equal=TRUE )


# Define plot colors
myBlue <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue25")
myRed <- rgb(255, 0, 0, max = 255, alpha = 50, names = "red25")

png("C:\\Users\\zloschin\\Documents\\APNEA_Project\\T_Test_Graphs\\Controls_Osa_vs_nonOSA.png")
freqValuesOSA = na.omit(freqValuesOSA)
freqValuesnonosa= na.omit(freqValuesnonosa)
hist(freqValuesOSA, col=myRed, breaks=25, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Controls: Osa Vs NonOSA Comparison \nT-Test P-val =", 
                  round(testResult$p.value, digits=3), 
                  "\n", "DF =", testResult$parameter))

lines(density(freqValuesOSA), col='red')

hist(freqValuesnonosa, col=myBlue, breaks=25, xlab="Spindle Frequency", 
     ylab="Number of Patients",
     main = paste("Controls: Osa Vs NonOSA Comparison \nT-Test P-val =", 
                  round(testResult$p.value, digits=3), 
                  "\n", "DF =", testResult$parameter), add=TRUE)

lines(density(freqValuesnonosa), col='blue')
legend("topright", c("OSA", "NonOSA"), fill=c("red", "blue"))
dev.off()

# Check for control normality
qqnorm(freqValuesOSA, main='Control: Osa Check for Normality')
qqline(freqValuesOSA)

qqnorm(freqValuesnonosa, main='Control: NonOSA Check for Normality')
qqline(freqValuesnonosa)
