# CTDcompare
Compare 3 different instruments (CTDs in this example) measuring similar parameters. Output statistcis and graphics on pdf page for each parameter + independant plot + idependant csv file with statistics.

Say one instrument is your reference and you want to check the performances of the other 2 against this reference. That could be it.
Here we want to compare two RBR Maestro against one SBE 19+ during a stabilization at 2m depth during 5 min approx.


At the moment, the script is formatted to read specific input files with date format YYYY-MM-DD HH:MM:SS,000.

You can adapt this script for other types of measurements, other parameters by changing the names of the parameters, units and nominal accuracies in the main.py.
main.py reads the csv files, create the dataframes and contain the parameters to check.
functions.py contains a couple of functions that are called in the main.

Hope it helps somenone. Cheers.

[Temperature__comparison_stats.csv](https://github.com/user-attachments/files/17165125/Temperature__comparison_stats.csv)
Instrument statistics,Mean,Standard Deviation
Temperature_ - Instrument Stats,,
Temperature_rbr231853,16.4553,0.0012
Temperature_rbr236135,16.4554,0.0009
Temperature_sbeSOMLIT,16.4531,0.0008
Mean of Differences and RMSE,Mean of Differences,RMSE
Temperature_rbr231853 - Temperature_rbr236135,-0.0001,0.0012
Temperature_rbr231853 - Temperature_sbeSOMLIT,0.0022,0.0024
Temperature_rbr236135 - Temperature_sbeSOMLIT,0.0023,0.0025

[Temperature__comparison_stats.pdf](https://github.com/user-attachments/files/17165119/Temperature__comparison_stats.pdf)
![Temperature__plot](https://github.com/user-attachments/assets/810cd621-48de-4b17-a541-f08430fab33a)
