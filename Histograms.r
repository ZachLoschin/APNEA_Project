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
for(i in 8:12){
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

# Import data for comparison charts
casePath = "Z:\\ResearchHome\\ClusterHome\\zloschin\\Spindle_Percent_Data\\Case_Percent_Data.xlsx"
controlPath = "Z:\\ResearchHome\\ClusterHome\\zloschin\\Spindle_Percent_Data\\Control_Percent_Data.xlsx"
caseData = read_excel(casePath)
controlData = read_excel(controlPath)

# Set up path for plot storage
histpath = "C:\\Users\\zloschin\\Documents\\APNEA_Project\\Comparagrams"

# Create comparagrams for each sleep state
name = names(caseData)

for(i in 3:7){
  # Define data to plot
  toPlotCase = as.numeric(unlist(caseData[ , i]))
  toPlotControl = as.numeric(unlist(my_data[ , i]))
  
  # Get the state name
  state = unlist(c(strsplit(name[i], split="_")))[1]
  
  # Define graphing parameters
  title = paste("Comparison of", state, "btwn Cases and Controls")
  xLabel = paste("Fraction of spindles in", state, "State")
  yLabel = "Number of Patients"
  filename = paste(histpath, "\\Comp_", name[i], ".png", sep="")
  breaks = 25
  
  # Call plot function
  plotCompareDistribution(x=toPlotControl, y=toPlotCase, xlabel=xLabel, ylabel = yLabel, title=title, filenam = filename, breks=breaks)
}

for(i in 8:12){
  # Define data to plot
  toPlotCase = as.numeric(unlist(caseData[ , i]))
  toPlotControl = as.numeric(unlist(my_data[ , i]))
  
  # Get the state name
  state = unlist(c(strsplit(name[i], split="_")))[1]
  
  # Define graphing parameters
  title = paste("Comparison of", state, "btwn Cases and Controls")
  xLabel = paste("Fraction of time in", state, "State")
  yLabel = "Number of Patients"
  filename = paste(histpath, "\\CompTime_", name[i], ".png", sep="")
  breaks = 25
  
  # Call plot function
  plotCompareDistribution(x=toPlotControl, y=toPlotCase, xlabel=xLabel, ylabel = yLabel, title=title, filenam = filename, breks=breaks)
}

# Define list of files
file_list <- list.files(path="Z:\\ResearchHome\\ClusterHome\\zloschin\\Cases_Excel_Data")

freqValuesCases = c()

for(j in 1:length(file_list)){
  
  # Read in excel
  tempDF <- read_excel(file_list[i])
  cat(paste("Read", i))
  
  # Initialize array for specific patients Hz values
  patientHz = c()
  
  for(i in 1:nrow(tempDF)){
    # Check if proper sleep state
    if(tempDF[i,22] == 2 || tempDF[i,22] == 1){
      if(tempDF[i,9] <= 12.5)
        patientHz = append(patientHz, as.numeric(tempDF[i, 9]))
    }
  }
  freqValues = append(freqValues, patientHz)
}










