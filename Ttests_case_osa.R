# Zachary Loschinskey
# St. Jude Children's Research Hospital
# Department of Diagnostic Imaging, Ranga Group
# statistical Analysis for Sleep Apnea Project
# 1 July 2022

# This script is for the t test analysis of case vs control and
# OSA vs non-OSA spindle frequency data


# Function definitions
plotDistribution = function (x, title, xlabel, ylabel, filenam, breks) {
  # Function to plot histogram + line
  N = length(x)
  x <- na.omit(x)
  png(filename = filenam)
  hist( x,col = "light blue",
        # probability = TRUE,
        main=title,
        xlab=xlabel,
        ylab=ylabel,
        xlim=c(0, 1),
        ylim=c(0, 80),
        breaks=breks)
  lines(density(x), col = "blue", lwd = 3)
  rug(x)
  print(N-length(x))
  dev.off()
}

plotCompareDistribution = function (x, y, title, xlabel, ylabel, filenam, breks){
  # Define transparent colors for easy visualization
  myBlue <- rgb(0, 0, 255, max = 255, alpha = 64, names = "blue25")
  myRed <- rgb(255, 0, 0, max = 255, alpha = 64, names = "red25")
  
  # Get rid of missing values
  x <- na.omit(x)
  y <- na.omit(y)
  
  # Create file for saving
  png(filename=filenam)
  
  # Plot first histogram with given parameters
  hist(x,col = myBlue,
       main = title,
       xlab=xlabel,
       ylab=ylabel,
       xlim=c(0,1),
       ylim=c(0,80),
       breaks=breks)
  # Plot line
  lines(density(x), col="blue", lwd=3)
  
  # Plot second histogram with given parameters
  hist(y,col=myRed,
       main = title,
       xlab=xlabel,
       ylab=ylabel,
       xlim=c(0,1),
       ylim=c(0,80),
       breaks=breks,
       add=TRUE)
  # Plot line
  lines(density(y), col="red", lwd=3)
  legend("topright", c("Case", "Control"), fill=c("red", "blue"))
  
  # Clear figure
  dev.off()
  
}

# Import library to read Excel files
library("readxl")

# Set up path to excel files
datapath = "C:\\Users\\zloschin\\Excel_Data_All\\Percentage_Data_Subset2.xlsx"

# Set up path for plot storage
histpath = "C:\\Users\\zloschin\\Documents\\APNEA_Project\\Histograms"

# Import data
my_data <- read_excel(path = datapath)

my_data2 = as.data.frame(my_data)

# Create histograms for percent spindles in each state
name = names(my_data)

# Define list of files
file_list_cases <- list.files(path="Z:/ResearchHome/ClusterHome/zloschin/Spind_Data_Case_Controls/Cases_Excel_Data",
                        full.names = TRUE,
                        recursive = TRUE)

freqValuesCases <- c()

for(i in 1:length(file_list_cases)){
  # Read in excel
  tempDF <- read_excel(file_list_cases[i])
  tempDF <- as.data.frame(tempDF)
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  tempDF3 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  freqs <- mean(tempDF3$Frequency, na.rn=TRUE)
  freqValuesCases[i] = freqs
  
}

# Define list of files
file_list_cont <- list.files(path="Z:/ResearchHome/ClusterHome/zloschin/Spind_Data_Case_Controls/Controls_Excel_Data",
                        full.names = TRUE,
                        recursive = TRUE)

freqValuesControls <- c()

for(i in 1:length(file_list_cont)){
  # Read in excel
  tempDF <- read_excel(file_list_cont[i])
  tempDF <- as.data.frame(tempDF)
  tempDF2 <- tempDF[tempDF$State == 1 | tempDF$State == 0 , ]
  tempDF3 <- tempDF2[tempDF2$Frequency <= 12.5 , ]
  
  freqs <- mean(tempDF3$Frequency, na.rn=TRUE)
  freqValuesControls = append(freqValuesCases, freqs)
  
}

# freqValuesCases and freqValuesControls, do t-test
testResult = t.test(freqValuesCases, freqValuesControls)


# OSA vs non-OSA comparison



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

plotCompareDistribution(x = freqValuesOSA, y = freqValuesnonosa, 
                        xlabel="Frequency (Hz)", ylabel = "Distribution", 
                        filenam="test.png", breks = 25, title = "Dist")


# png(filename = "test.png")
# freqValuesOSA = na.omit(freqValuesOSA)
# hist(freqValuesOSA)
# lines(density(freqValuesOSA))
# 
# dev.off()


