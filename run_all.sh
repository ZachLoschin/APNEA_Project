# Shell Interpreter
#!/bin/bash

# Runing spindle detection again with 1.5RMS threshold. Then I will recalculate the extraction features and coupling.

# Spindle detection
python Block2_Spindle_Detection.py

# Slow wave detection
python Block4_Slow_Wave_Detection.py

# Extract Features
python Block5_Extract_Spindles_SW_Features.py

# Coupling Calculations
python Coupling_calculations.py