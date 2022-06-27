# Zachary Loschinskey
# St. Jude Children's Research Hospital
# Department of Diagnostic Imaging, Ranga Group
# statistical Analysis for Sleep Apnea Project


# Function definitions
plotDistribution = function (x, title, xlabel, ylabel, filenam, breks) {
  # Function to plot histogram + line
  N = length(x)
  x <- na.omit(x)
  png(filename = filenam)
  hist( x,col = "light blue",
        probability = TRUE,
        main=title,
        xlab=xlabel,
        ylab=ylabel, 
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
  title = name[i]
  xLabel = "Fraction of Spindles in Title State"
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
  title = name[i]
  xLabel = "Fraction of Spindles in Title State"
  yLabel = "Number of Patients"
  filename = paste(histpath, "\\Hist_", name[i], ".png", sep="")
  breaks = 25
  
  # Call my distribution function
  plotDistribution(toPlot, title, xLabel, yLabel, filename, breaks)
}





# for(i in 3:7){
#   hist(my_data[, i], col=colors[i-2], add=TRUE)
# }
# legend('topright', c('W', 'R', 'N3', "N2", "N1"), fill=colors())

NoMissing <- my_data[,3][!is.na(my_data[,3])]



