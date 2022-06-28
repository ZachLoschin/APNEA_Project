# Zachary Loschinskey
# St. Jude Children's Research Hospital
# Department of Diagnostic Imaging, Ranga Group
# statistical Analysis for Sleep Apnea Project
# 6 June 2022


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

# Import library to read Excel files
library("readxl")

# Set up path to excel files
datapath = "C:\\Users\\zloschin\\Excel_Data_All\\Percentage_Data_Subset2.xlsx"

# Set up path for plot storage
histpath = "C:\\Users\\zloschin\\Documents\\APNEA_Project\\Histograms"

# Import data
my_data <- read_excel(path = datapath)

# Create histograms for percent spindles in each state
name = names(my_data)
for(i in 3:7){
  # Prepare inputs for dist function
  toPlot = as.numeric(unlist(my_data[ , i]))
  state = unlist(c(strsplit(name[i], split="_")))[1]
  title = paste("Fraction of Total Spindles detected in", state, "State")
  xLabel = paste("Fraction of Spindles in", state, "State")
  yLabel = "Number of Patients"
  filename = paste(histpath, "\\Hist_", name[i], ".png", sep="")
  breaks = 25
  
  # Call my distribution function
  plotDistribution(toPlot, title, xLabel, yLabel, filename, breaks)
}

# Create histograms for percent time in each state
for(i in 7:ncol(my_data)){
  # Prepare inputs for dist function
  toPlot = as.numeric(unlist(my_data[ , i]))
  state = unlist(c(strsplit(name[i], split="_")))[1]
  title = paste("Fraction of Total Time Spent in", state, "State")
  xLabel = paste("Fraction of time spent in", state, "State")
  yLabel = "Number of Patients"
  filename = paste(histpath, "\\Hist_", name[i], ".png", sep="")
  breaks = 25
  
  # Call my distribution function
  plotDistribution(toPlot, title, xLabel, yLabel, filename, breaks)
}

