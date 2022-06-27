# Zachary Loschinskey
# St. Jude Children's Research Hospital
# Department of Diagnostic Imaging, Ranga Group
# 
# statistical Analysis for Sleep Apnea Project

# Import library to read Excel files
library("readxl")

# Set up path to excel files
datapath = "C:\\Users\\zloschin\\Excel_Data_All\\Percentage_Data_Subset2.xlsx"

# Set up path for plot storage
histpath = "C:\\Users\\zloschin\\Documents\\APNEA_Project\\Histograms"

# Import data
my_data <- read_excel(path = datapath)

# Create histograms for each column
name = names(my_data)
for(i in 3:ncol(my_data)){
  png(filename = paste(histpath, "\\Hist_", name[i], ".png", sep=""))
  hist(my_data[, i])
  dev.off()
}

# Create multiple histogram plot for spindle percentages
colors = c('red', 'coral', 'blue', 'chocolate', 'deeppink')
png(filename = paste(histpath, "\\Spindle_Percents", ".png", sep=""))
for(i in 3:7){
  hist(my_data[, i], col=colors[i-2], add=TRUE)
}
legend('topright', c('W', 'R', 'N3', "N2", "N1"), fill=colors())
dev.off()



