# XRD Scripts tutorials
In this document I will explain the possible functions for XRD data analysis and plotting.
## XRD plotting
In this section I will discuss the script for plotting of XRD spectra  obtained from XRD devices here at FZU (**XRD_plotting.py**). They are in files with format **.xy** in which the first column is the angle and the second column is the intensity. I will now explain the lines of code, that are necessary to change for the use of this script.
### Loading the data
```
#data sets
    #435 C
XRD_435c_2 = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\O2-02sccm_13min_435C.xy")
...
#XRD Data sets
SnO = np.loadtxt(r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\SnO_XRD.txt", delimiter=',',skiprows=1, dtype={'names': ('label', 'd_spacing', 'position'),
                                                           'formats': ('U10', 'f4', 'f4')})
plane_labels = SnO['label']
plane_positions = SnO['position']
```
There are two main sections for the loading of the data files. First there is the section with _#data sets_, where you load all of the data sets from XRD. Here you load it in to variable with the name **XRD_435C_2** which is then used in plt. functions. As the .xy files do not have any complicated formmating, it is easily loaded just by inputing the address.
The second section loads the data sets with the information of Miller indices of the planes, d_spacing and position of the peaks calculated using the script **Miller_indices.py**. As this program outputs this file in this format, it is just needed to rewrite the address of the file and if you have multiple compounds, then also change the names of the variables _plane_labels and plane_positions_, which are then used to plot these positions and names in to graphs.
### Moving constant
```
#Moving constant
a = 100
```
This variable is used just for positioning of the spectra in the graphs, i.e. if the you input multiple spectra in to one graphs, you add some multiple of this variable to _y_ coordinate so the do not overlap.
### Main plotting script
```
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
```
Here is the main block of plotting one graph, from top to bottom it has several things that can be changed. In first row, the _fig size_ is the command for the size of the figure it outputs, for more precise dimensions, it need to be looke up, what to input there, i.e. for the best size for articles. Then there are rows for the titles and labes of axis, with font sizes you can change the size of the letters. Be aware, when the font size of y-axis name is to big, it can be cut in the final fig. Next command change how the axis looks like, if there should be minor ticks, how big should they be, or from which values should the graph be showcased in the x and y axis. Quite usefull when zou also output multiple Miller indices.
```
plt.plot(XRD_435c_2[:,0], XRD_435c_2[:, 1], marker='.', markersize=1, color='darkblue', label='2 sccm', lw=2)
```
This is basic command for plotting one measured spectra. _XRD_435c_2[:,0], XRD_435c_2[:, 1]_ signifies the data found in the .xy file for x and y axis, _marker='.', markersize=1_ these command just makes it, that it is smooth line, _color='darkblue'_ with this command you can change the colours of the spectra, for reference look up coulours plt and you will find either the names or codes for the colours, _label='2 sccm'_ this is the name corresponding to this spectra in the legend, make it simple, _lw=2_ this command changes the width of the final line.
```
for label, pos in zip(plane_labels, plane_positions):
    plt.axvline(x=pos, color='b', linestyle='--', linewidth=1, alpha = 0.5)  # Draw vertical lines
    plt.text(pos, 3300, f'{label}',
             rotation=90, verticalalignment='bottom', horizontalalignment='right', fontsize=20, color = 'b')
```
Now comes the command for plotting the positions of the corresponding Miller indices with the names of the planes next to the lines. In the first row you input the variables created in the data sets. The second row creates dashed vertical line at position from the loaded file, with wanted colour, linewidth and alpha, which signifies how transparent the line will be (from 0 being fully transparent to 1 being solid). Third and fourth row creates a name of the miller plane next to the corresponding line. The _pos_ takes the position from the data set, the next number _3300_ is the y-axis position of the first symbol and the last command on the third row takes the name of the miller plane and prints it. The last row rotates the name by some angle and then you can change the allignment, vertical is, if you want to start at position 3300, i.e. bottom, or end at that position, i.e. top. Horizontal allignment is if you want to have it on the left or right of the line, for more information about allignment, you can search _text allignment plt_. Then again, there are command for the font size and colour of the text.
```
plt.axvline(x=18.34, color='b', linestyle='--', linewidth=1, alpha = 0.5, label='SnO')  # Draw vertical lines
```
This is command, so it creates a label in the legend, due to problem with implementing this in the part about creating these line in the for cycle. If label is placed in that part, it will create duplicates of the same name in the legend, therefore this just creates duplicate of one line on one of the positions and then is added in to the legend list. Therefore keep the same parameters of the line as in the for cycle above.
```
plt.legend(loc="best", borderaxespad=0, bbox_to_anchor=(1, 1), fontsize=20)
plt.grid(color='black', linestyle='dashed', linewidth=0.5)
```
This prints legend in the graph, be aware, location is quite tricky and depends on white spaces and the size of the legend, therefore by specifing with the command _bbox_to_anchor=(1, 1)_ this puts it outside of the xy area on the right side. By including the _grid_ command, grid can be added. In the .py file you can find two types of graphs, one without grid is commented.
If more graphs are needed, duplicate the commands from _plt.figure_ to _plt.show()_ which creates seperate windows.

## XRD Miller indeces calculation
At this moment this script is quite simple and can calculate only Miller indices, interplanar spacing and corresponding angle for XRD measurement. I might add more functions to be able to calculate all possible crystal structures.
```
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
```
Firstly, one needs the lattice parameters **_a, b, c_**, this can be found in articles or some tables. Depending on the type unit cell, you need all of them or just few of them, when the angles are not 90deg then you will also need the angles. You input it in Å. Then you need the length of the xray _CuKa_, which is defined by the source.
Then there is the script itself, first it creates .txt file in the designated address, afterwhich it eneters in to three for cycles, which corresponds to the miller indices, where you can change to which extent you want to calculate with the _range_ parameter. When every index is zero, it first writes a header in to the document. Because indexes _h_ and _k_ cannot be distinguished, it skips one possible combination of them as not to duplicate results. If no other condition is obstructing, then it calculates the interplanar spacing and the angle and prints them in the document. This cycles until all for cycles are finished.
