# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 22:39:14 2024

@author: tmase
"""

import numpy as np
import matplotlib.pyplot as plt
#import pandas as pd
#import math as mt
#from scipy import constants as con

#data sets
    #435 C
XRD_435c_2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2-02sccm_13min_435C.xy")   
XRD_435c_5 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_5sccm_A_435C_glass.xy")
XRD_435c_10 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_10sccm_A_435C_glass.xy")    
XRD_435c_15 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_15sccm_A_435C_glass.xy")    
XRD_435c_20 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_20sccm_A_435C_glass.xy")    
XRD_435c_25 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_25sccm_glass_435C.xy") 

#Moving constant
a = 100


#XRD Data sets

SnO = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\SnO_XRD.txt", delimiter=',',skiprows=1, dtype={'names': ('label', 'd_spacing', 'position'),
                                                           'formats': ('U10', 'f4', 'f4')})
plane_labels = SnO['label']
plane_positions = SnO['position']

SnO2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\SnO2_XRD.txt", delimiter=',',skiprows=1, dtype={'names': ('label', 'd_spacing', 'position'),
                                                           'formats': ('U10', 'f4', 'f4')})
plane_labels2 = SnO2['label']
plane_positions2 = SnO2['position']


#XRD spektroskopie


    #Vyvoj pro 435 C
plt.figure(figsize=(12, 9))
plt.title('XRD, change of spectra for 435 °C', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.ylim(-100,3900)
plt.minorticks_on()
plt.plot(XRD_435c_2[:,0], XRD_435c_2[:, 1], marker='.', markersize=1, color='darkblue', label='2 sccm', lw=2)
plt.plot(XRD_435c_5[:,0], 5*a+XRD_435c_5[:, 1], marker='.', markersize=1, color='red', label='5 sccm', lw=2)
plt.plot(XRD_435c_10[:,0], 10*a+XRD_435c_10[:, 1], marker='.', markersize=1, color='darkgreen', label='10 sccm', lw=2)
plt.plot(XRD_435c_15[:,0], 15*a+XRD_435c_15[:, 1]/2, marker='.', markersize=1, color='magenta', label='15 sccm', lw=2)
plt.plot(XRD_435c_20[:,0], 20*a+XRD_435c_20[:, 1], marker='.', markersize=1, color='darkorange', label='20 sccm', lw=2)
plt.plot(XRD_435c_25[:,0], 25*a+XRD_435c_25[:, 1], marker='.', markersize=1, color='saddlebrown', label='25 sccm', lw=2)
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 3300, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 3550, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="best", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()

'''
# set tick width
mpl.rcParams['xtick.major.size'] = 13
mpl.rcParams['xtick.major.width'] = 4
mpl.rcParams['xtick.minor.size'] = 8
mpl.rcParams['xtick.minor.width'] = 2
mpl.rcParams['ytick.major.size'] = 13
mpl.rcParams['ytick.major.width'] = 4
mpl.rcParams['ytick.minor.size'] = 8
mpl.rcParams['ytick.minor.width'] = 2
mpl.rcParams['axes.linewidth'] = 3


    #Vyvoj pro 435 C
plt.figure(figsize=(13, 10))
#plt.title('XRD, change of spectra for 435 °C', fontsize=30)
plt.xlabel(r'$2\theta$ [deg]', fontsize=30)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.ylim(-100,3900)
plt.minorticks_on()
plt.plot(XRD_435c_2[:,0], XRD_435c_2[:, 1], marker='.', markersize=1, color='darkblue', label='2 sccm', lw=2)
plt.plot(XRD_435c_5[:,0], 5*a+XRD_435c_5[:, 1], marker='.', markersize=1, color='red', label='5 sccm', lw=2)
plt.plot(XRD_435c_10[:,0], 10*a+XRD_435c_10[:, 1], marker='.', markersize=1, color='darkgreen', label='10 sccm', lw=2)
plt.plot(XRD_435c_15[:,0], 15*a+XRD_435c_15[:, 1]/2, marker='.', markersize=1, color='magenta', label='15 sccm', lw=2)
plt.plot(XRD_435c_20[:,0], 20*a+XRD_435c_20[:, 1], marker='.', markersize=1, color='darkorange', label='20 sccm', lw=2)
plt.plot(XRD_435c_25[:,0], 25*a+XRD_435c_25[:, 1], marker='.', markersize=1, color='saddlebrown', label='25 sccm', lw=2)
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 3300, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 3550, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="best", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=25)
plt.show()

'''