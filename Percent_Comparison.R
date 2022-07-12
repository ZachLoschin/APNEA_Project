# Zachary Loschinskey
# St. Jude Children's Research Hospital
# Department of Diagnostic Imaging, Ranga Group
# 7/12/2022

# Creating line graphs of our detected sleep perentages vs the slepe reports

# Import library to read Excel files
library("readxl")

# Define data path
data = "Z:\\ResearchHome\\ClusterHome\\zloschin\\Spindle_Percent_Data\\Percent_Data_combined.xlsx"

# Import the data
DF <- read_excel(data)

# Convert to data frame
DF <- as.data.frame(DF)

# Plot W line graph
png(file="C:\\Users\\zloschin\\Documents\\APNEA_Project_New\\State_Comparisons\\W_Percent.png")
plot(DF$W_Time, type="o", col="red", ylab="Fraction in Wake", xlab="Patient",
     main="Percent W Classification Comparison", ylim=c(0,1))
lines(DF$Rep_W, type="o", col="blue")
legend("topright", c("Our States", "Sleep Report States"), fill=c("red", "blue"))
dev.off()

# Plot R line graph
png(file="C:\\Users\\zloschin\\Documents\\APNEA_Project_New\\State_Comparisons\\REM_Percent.png")
plot(DF$REM_Time, type="o", col="red", ylab="Fraction in Wake", xlab="Patient",
     main="Percent REM Classification Comparison", ylim=c(0,1))
lines(DF$Rep_R, type="o", col="blue")
legend("topright", c("Our States", "Sleep Report States"), fill=c("red", "blue"))
dev.off()

# Plot N1 line graph
png(file="C:\\Users\\zloschin\\Documents\\APNEA_Project_New\\State_Comparisons\\N1_Percent.png")
plot(DF$N1_Time, type="o", col="red", ylab="Fraction in Wake", xlab="Patient",
     main="Percent N1 Classification Comparison", ylim=c(0,1))
lines(DF$Rep_N1, type="o", col="blue")
legend("topright", c("Our States", "Sleep Report States"), fill=c("red", "blue"))
dev.off()

# Plot N2 line graph
png(file="C:\\Users\\zloschin\\Documents\\APNEA_Project_New\\State_Comparisons\\N2_Percent.png")
plot(DF$N2_Time, type="o", col="red", ylab="Fraction in Wake", xlab="Patient",
     main="Percent N2 Classification Comparison", ylim=c(0,1))
lines(DF$Rep_N2, type="o", col="blue")
legend("topright", c("Our States", "Sleep Report States"), fill=c("red", "blue"))
dev.off()

# Plot N3 line graph
png(file="C:\\Users\\zloschin\\Documents\\APNEA_Project_New\\State_Comparisons\\N3_Percent.png")
plot(DF$N3_Time, type="o", col="red", ylab="Fraction in Wake", xlab="Patient",
     main="Percent N3 Classification Comparison", ylim=c(0,1))
lines(DF$Rep_N3, type="o", col="blue")
legend("topright", c("Our States", "Sleep Report States"), fill=c("red", "blue"))
dev.off()
