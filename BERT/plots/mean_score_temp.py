
"""
This file will contain a mean score plot script from the file json_score_temp.csv
It will print the mean for each temp and the mean for each (temp, file) pair
The data file contain score for each configuration of each file with the three temperatures 0.5, 0.7, 1.0
with three runs per configuration to compute the mean

Configuration codage (TestID column in csv)
I/S (infected or safe) 0-6 data file representation, 0-3 prompt ID, 0-5 Documentation version, 00-20 Temperature
Example: 
        - I02310 Infected ,file full_local.json, Prompt 2, Documentation 3, Temperature=1.0, 
        - S30105 Safe, file ls_kill.json, prompt 0, documentation 1, Temperature = 0.5 
""" 