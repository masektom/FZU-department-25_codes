# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 22:39:14 2024

@author: tmase
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#import math as mt
#from scipy import constants as con
#data sets
    #20 C
XRD_20c_0 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_0sccm_glass.xy")
XRD_20c_2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_2sccm_glass.xy")
XRD_20c_5 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_5sccm_glass.xy")
XRD_20c_10 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_10sccm_glass.xy")
XRD_20c_15 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_15sccm_glass.xy")
XRD_20c_20 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2-20sccm_25min_RT.xy")
XRD_20c_25 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_25sccm_A_glass.xy")
XRD_20c_50 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_50sccm_glass.xy")
    #350 C
XRD_350c_2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2-02sccm_13min_350C.xy")   
XRD_350c_5 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_5sccm_A_350C_glass.xy")
XRD_350c_10 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_10sccm_A_350C_glass.xy")
XRD_350c_15 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_15sccm_A_350C_glass.xy")
XRD_350c_20 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_20sccm_A_350C_glass.xy")
XRD_350c_25 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_25sccm_A_350C_glass.xy")
    #435 C
XRD_435c_2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2-02sccm_13min_435C.xy")   
XRD_435c_5 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_5sccm_A_435C_glass.xy")
XRD_435c_10 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_10sccm_A_435C_glass.xy")    
XRD_435c_15 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_15sccm_A_435C_glass.xy")    
XRD_435c_20 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_20sccm_A_435C_glass.xy")    
XRD_435c_25 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2_25sccm_glass_435C.xy") 
    #20 C zihani
XRD_zih_20c_0 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Zihani_435C_4h_RT_00sccm.xy")
XRD_zih_20c_2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Zihani_435C_4h_RT_02sccm.xy")
XRD_zih_20c_5 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Zihani_435C_4h_RT_05sccm.xy")
XRD_zih_20c_10 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Zihani_435C_4h_RT_10sccm.xy")
XRD_zih_20c_15 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Zihani_435C_4h_RT_15sccm.xy")
XRD_zih_20c_20 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Zihani_435C_4h_RT_90sccm.xy")
XRD_zih_20c_25 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Zihani_435C_4h_RT_25sccm.xy")
#XRD_zih_20c_50 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Zihani_435C_4h_RT_90sccm.xy")  
#Posouvaci konstanta
a = 100

#XRD Data sets
#SnO2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\SnO2_XRD.txt", delimiter=',', skiprows=1)

SnO = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\SnO_XRD.txt", delimiter=',',skiprows=1, dtype={'names': ('label', 'd_spacing', 'position'),
                                                           'formats': ('U10', 'f4', 'f4')})
plane_labels = SnO['label']
plane_positions = SnO['position']

SnO2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\SnO2_XRD.txt", delimiter=',',skiprows=1, dtype={'names': ('label', 'd_spacing', 'position'),
                                                           'formats': ('U10', 'f4', 'f4')})
plane_labels2 = SnO2['label']
plane_positions2 = SnO2['position']

Sn = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\Sn_XRD.txt", delimiter=',',skiprows=1, dtype={'names': ('label', 'd_spacing', 'position'),
                                                           'formats': ('U10', 'f4', 'f4')})
plane_labelsSn = Sn['label']
plane_positionsSn = Sn['position']

#XRD spektroskopie

#prutok 2 sccm
plt.figure(figsize=(12, 9))
plt.title('XRD, Comparison for Q = 2 sccm', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.minorticks_on()
plt.plot(XRD_20c_2[:,0], -a+XRD_20c_2[:, 1], marker='.', markersize=1, color='darkblue', label='RT', lw=2)
plt.plot(XRD_350c_2[:,0], 4*a+XRD_350c_2[:, 1], marker='.', markersize=1, color='darkgreen', label='350C', lw=2)
plt.plot(XRD_435c_2[:,0], 9*a+XRD_435c_2[:, 1], marker='.', markersize=1, color='red', label='435C', lw=2)
plt.plot(XRD_zih_20c_2[:,0], 14*a+XRD_zih_20c_2[:, 1], marker='.', markersize=1, color='orange', label='RT annealed', lw=2)
for label, pos in zip(plane_labelsSn, plane_positionsSn):
    plt.axvline(x=pos, color='black', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, -250, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'black')
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 3500, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 3800, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=30.77, color='black', linestyle='--', linewidth=1, alpha = 0.5, label='Sn')  # Draw vertical lines
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="upper right", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=17)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()




    #prutok 5 sccm
plt.figure(figsize=(12, 9))
plt.title('XRD, Comparison for Q = 5 sccm', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.minorticks_on()
plt.plot(XRD_20c_5[:,0], -a+XRD_20c_5[:, 1], marker='.', markersize=1, color='darkblue', label='RT', lw=2)
plt.plot(XRD_350c_5[:,0], 4*a+XRD_350c_5[:, 1], marker='.', markersize=1, color='darkgreen', label='350C', lw=2)
plt.plot(XRD_435c_5[:,0], 9*a+XRD_435c_5[:, 1], marker='.', markersize=1, color='red', label='435C', lw=2)
plt.plot(XRD_zih_20c_5[:,0], 14*a+XRD_zih_20c_5[:, 1], marker='.', markersize=1, color='orange', label='RT annealed', lw=2)
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 3500, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 3800, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="upper right", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=17)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()


    #prutok 10 sccm
plt.figure(figsize=(12, 9))
plt.title('XRD, Comparison for Q = 10 sccm', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
#plt.xlim(0,300)
plt.minorticks_on()
plt.plot(XRD_20c_10[:,0], -0.5*a+XRD_20c_10[:, 1], marker='.', markersize=1, color='darkblue', label='RT', lw=2)
plt.plot(XRD_350c_10[:,0], 1.5*a+XRD_350c_10[:, 1], marker='.', markersize=1, color='darkgreen', label='350C', lw=2)
plt.plot(XRD_435c_10[:,0], 3.5*a+XRD_435c_10[:, 1], marker='.', markersize=1, color='red', label='435C', lw=2)
plt.plot(XRD_zih_20c_10[:,0], 5.5*a+XRD_zih_20c_10[:, 1], marker='.', markersize=1, color='orange', label='RT annealed', lw=2)
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 1000, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 1080, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.legend(loc="upper right", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()

    #prutok 15 sccm
plt.figure(figsize=(12, 9))
plt.title('XRD, Comparison for Q = 15 sccm', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.ylim(-200,4500)
plt.minorticks_on()
plt.plot(XRD_20c_15[:,0], -a+XRD_20c_15[:, 1], marker='.', markersize=1, color='darkblue', label='RT', lw=2)
plt.plot(XRD_350c_15[:,0], 10*a+XRD_350c_15[:, 1], marker='.', markersize=1, color='darkgreen', label='350C', lw=2)
plt.plot(XRD_435c_15[:,0], 20*a+XRD_435c_15[:, 1]/2, marker='.', markersize=1, color='red', label='435C', lw=2)
plt.plot(XRD_zih_20c_15[:,0], 30*a+XRD_zih_20c_15[:, 1], marker='.', markersize=1, color='orange', label='RT annealed', lw=2)
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 3880, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 4200, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="upper right", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()


    #prutok 20 sccm
plt.figure(figsize=(12, 9))
plt.title('XRD, Comparison for Q = 20 sccm', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.ylim(-100,1650)
plt.minorticks_on()
plt.plot(XRD_20c_20[:,0], -0.6*a + XRD_20c_20[:, 1], marker='.', markersize=1, color='darkblue', label='RT', lw=2)
plt.plot(XRD_350c_20[:,0], 2.5*a+XRD_350c_20[:, 1], marker='.', markersize=1, color='darkgreen', label='350C', lw=2)
plt.plot(XRD_435c_20[:,0], 5*a+XRD_435c_20[:, 1], marker='.', markersize=1, color='red', label='435C', lw=2)
plt.plot(XRD_zih_20c_20[:,0], 8.3*a+XRD_zih_20c_20[:, 1], marker='.', markersize=1, color='orange', label='RT annealed', lw=2)
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 1300, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 1400, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="upper right", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()


    #prutok 25 sccm
plt.figure(figsize=(12, 9))
plt.title('XRD, Comparison for Q = 25 sccm', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.ylim(-100,1700)
plt.minorticks_on()
plt.plot(XRD_20c_25[:,0], -0.5*a+XRD_20c_25[:, 1], marker='.', markersize=1, color='darkblue', label='RT', lw=2)
plt.plot(XRD_350c_25[:,0], 2*a+XRD_350c_25[:, 1], marker='.', markersize=1, color='darkgreen', label='350C', lw=2)
plt.plot(XRD_435c_25[:,0], 4.5*a+XRD_435c_25[:, 1], marker='.', markersize=1, color='red', label='435C', lw=2)
plt.plot(XRD_zih_20c_25[:,0], 6.7*a+XRD_zih_20c_25[:, 1], marker='.', markersize=1, color='orange', label='RT annealed', lw=2)
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 1450, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 1570, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="upper right", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()


    #Vyvoj pro RT
plt.figure(figsize=(12, 9))
plt.title('XRD, change of spectra for RT', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.ylim(-100,4800)
plt.minorticks_on()
plt.plot(XRD_20c_0[:,0], XRD_20c_0[:, 1]/5, marker='.', markersize=1, color='black', label='0 sccm', lw=2)
plt.plot(XRD_20c_2[:,0], 5*a+XRD_20c_2[:, 1], marker='.', markersize=1, color='darkblue', label='2 sccm', lw=2)
plt.plot(XRD_20c_5[:,0], 10*a+XRD_20c_5[:, 1], marker='.', markersize=1, color='red', label='5 sccm', lw=2)
plt.plot(XRD_20c_10[:,0], 15*a+XRD_20c_10[:, 1], marker='.', markersize=1, color='darkgreen', label='10 sccm', lw=2)
plt.plot(XRD_20c_15[:,0], 20*a+XRD_20c_15[:, 1], marker='.', markersize=1, color='magenta', label='15 sccm', lw=2)
plt.plot(XRD_20c_20[:,0], 25*a+XRD_20c_20[:, 1], marker='.', markersize=1, color='darkorange', label='20 sccm', lw=2)
plt.plot(XRD_20c_25[:,0], 30*a+XRD_20c_25[:, 1], marker='.', markersize=1, color='saddlebrown', label='25 sccm', lw=2)
plt.plot(XRD_20c_50[:,0], 35*a+XRD_20c_50[:, 1], marker='.', markersize=1, color='olive', label='50 sccm', lw=2)
for label, pos in zip(plane_labelsSn, plane_positionsSn):
    plt.axvline(x=pos, color='black', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 300, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'black')
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 4000, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 4350, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=30.77, color='black', linestyle='--', linewidth=1, alpha = 0.5, label='Sn')  # Draw vertical lines
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="best", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()


    #Vyvoj pro 350 C
plt.figure(figsize=(12, 9))
plt.title('XRD, change of spectra for 350 °C', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.ylim(-100,3800)
plt.minorticks_on()
plt.plot(XRD_350c_2[:,0], -a+XRD_350c_2[:, 1], marker='.', markersize=1, color='darkblue', label='2 sccm', lw=2)
plt.plot(XRD_350c_5[:,0], 4*a+XRD_350c_5[:, 1], marker='.', markersize=1, color='red', label='5 sccm', lw=2)
plt.plot(XRD_350c_10[:,0], 9*a+XRD_350c_10[:, 1], marker='.', markersize=1, color='darkgreen', label='10 sccm', lw=2)
plt.plot(XRD_350c_15[:,0], 14*a+XRD_350c_15[:, 1], marker='.', markersize=1, color='magenta', label='15 sccm', lw=2)
plt.plot(XRD_350c_20[:,0], 19*a+XRD_350c_20[:, 1], marker='.', markersize=1, color='darkorange', label='20 sccm', lw=2)
plt.plot(XRD_350c_25[:,0], 24*a+XRD_350c_25[:, 1], marker='.', markersize=1, color='saddlebrown', label='25 sccm', lw=2)
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 3200, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 3450, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="best", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()


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


    #Vyvoj pro RT annealed
plt.figure(figsize=(12, 9))
plt.title('XRD, change of spectra for RT annealed', fontsize=25)
plt.xlabel(r'$2\theta$ [deg]', fontsize=20)
plt.ylabel('Intensity [a.u.]', fontsize=25)
plt.xticks(size = 20)
plt.yticks(size=20)
plt.ylim(-100,4000)
plt.minorticks_on()
plt.plot(XRD_zih_20c_0[:,0], XRD_zih_20c_0[:, 1]/5, marker='.', markersize=1, color='black', label='0 sccm', lw=2)
plt.plot(XRD_zih_20c_2[:,0], 5*a+XRD_zih_20c_2[:, 1], marker='.', markersize=1, color='darkblue', label='2 sccm', lw=2)
plt.plot(XRD_zih_20c_5[:,0], 10*a+XRD_zih_20c_5[:, 1], marker='.', markersize=1, color='red', label='5 sccm', lw=2)
plt.plot(XRD_zih_20c_10[:,0], 15*a+XRD_zih_20c_10[:, 1], marker='.', markersize=1, color='darkgreen', label='10 sccm', lw=2)
plt.plot(XRD_zih_20c_15[:,0], 20*a+XRD_zih_20c_15[:, 1], marker='.', markersize=1, color='magenta', label='15 sccm', lw=2)
plt.plot(XRD_zih_20c_20[:,0], 25*a+XRD_zih_20c_20[:, 1], marker='.', markersize=1, color='darkorange', label='20 sccm', lw=2)
plt.plot(XRD_zih_20c_25[:,0], 30*a+XRD_zih_20c_25[:, 1], marker='.', markersize=1, color='saddlebrown', label='25 sccm', lw=2)
for label, pos in zip(plane_labelsSn, plane_positionsSn):
    plt.axvline(x=pos, color='black', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 200, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'black')
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 3500, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
for label2, pos2 in zip(plane_labels2, plane_positions2):
    plt.axvline(x=pos2, color='r', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos2, 3750, f'{label2}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'r')
plt.axvline(x=30.77, color='black', linestyle='--', linewidth=1, alpha = 0.5, label='Sn')  # Draw vertical lines
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
plt.axvline(x=33.91, color='r', linestyle='--', linewidth=1, alpha = 0.5, label=r'$SnO_2$')  # Draw vertical lines
plt.legend(loc="best", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
plt.show()
