# FZU codes
This is repository for all Python codes used on FZU created by Ing. Tomáš Mašek. It is divided in to several branches with main beeing the central hub where all updates about all of the branches will be written. There is high possibility, that there are some bugs, there are not yet addressed, therefore if something does not work, consult with me or internet.
# Updates
## 17.6.2026 - Repository made public
I have made several branches for my codes - XRD, Van der Pauw and Response of semiconductor on light. With it I added tutorials for the use of these scripts
### XRD
Script for plotting spectra obtained from XRD, Script for calculation of Muller indices for XRD (only for Tetragonal lattice)
### Van der Pauw
Script for Van der Pauw measurement, with tutorial and excel table for calculation of the resistivity and conductivity of films
### Response of semiconductors on light
Script for the measurement with examples of the graphs you can obtain, script for plotting the data obtained from script for the measurement with possible comparison and calculation of the decay time.

## 18.6.2026 - XRD lattice calculator
Replaced vypocet_rovin.py with XRD_lattice_calculation.py
### New functions
Before it was only calculation for Tetragonal lattice, now it is possible to calculate Muller indices, d_hkl and position 2theta for any Bravais lattice. Quickly looked through the formulas and they should be correct, but I did not yet test it for every type of lattice, therefore while using this script, check if the results are correct.
