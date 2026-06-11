# -*- coding: utf-8 -*-
# Vypocet XRD spekter
import numpy as np
import math as mt

theta = "\u03B8"  # Greek letter theta
a = 3.803 #Å - SnO
#a = 4.738 #Å - SnO2
c = 4.838 #Å - SnO
#c = 3.186 #Å - SnO2
CuKa = 1.54184 #Å
with open("C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\SnO_XRD.txt", "w") as file:  # Open a file in write mode
    for h in range(4):  # Outer loop (0 to 2)
        for k in range(4):  # Middle loop (0 to 2)
            for l in range(4):  # Inner loop (0 to 2)
                if h == 0 and k == 0 and l == 0:  # Check if all variables are zero
                    SnO_XRD = f"rovina, d_space, 2theta\n"
                else:
                    if k > h:
                        continue
                    else:
                        d = round((a*c)/np.sqrt(c**2*(h**2+k**2)+a**2*l**2), 5)
                        Th = round(mt.degrees(2*mt.asin(CuKa/(2*d))), 2)
                        SnO_XRD = f"({h}{k}{l}), {d}, {Th}\n"
                print(SnO_XRD.strip())  # Print to console
                file.write(SnO_XRD)  # Write to the file
'''              
                
with open("C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\SnO2_XRD.txt", "w") as file:  # Open a file in write mode
    for h in range(4):  # Outer loop (0 to 2)
        for k in range(4):  # Middle loop (0 to 2)
            for l in range(4):  # Inner loop (0 to 2)
                if h == 0 and k == 0 and l == 0:  # Check if all variables are zero
                    SnO2_XRD = f"rovina, d_space, 2theta\n"
                else:
                    if k > h:
                        continue
                    else:
                        d = round((a*c)/np.sqrt(c**2*(h**2+k**2)+a**2*l**2), 5)
                        Th = round(mt.degrees(2*mt.asin(CuKa/(2*d))), 2)
                        SnO2_XRD = f"({h}{k}{l}), {d}, {Th}\n"
                print(SnO2_XRD.strip())  # Print to console
                file.write(SnO2_XRD)  # Write to the file                          
                
'''                
                
                
                