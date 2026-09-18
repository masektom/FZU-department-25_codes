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
Using this code, it is possible to calculate any Bravaise lattice Miller indices, interplanar distance d_hkl and its position in XRD spectra.
Again, only parameters that needs to be changed are at the end of the script. Only one, that is at the start of the script is the wavelength of the source, as at FZU we use CuKa, it is made as standard for all the calculation below.
### Usage
```
# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    output_dir = r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\test"

    # SnO - tetragonal
    Tetragonal(a=3.803, c=4.838, directory=output_dir, number=3, filename="SnO_XRD_test.txt")

    # SnO2 - tetragonal (uncomment to use)
    # Tetragonal(a=4.738, c=3.186, directory=output_dir, number=3, filename="SnO2_XRD.txt")

    # Other lattice examples:
    # Cubic(a=4.065, directory=output_dir, number=3, filename="Al_XRD.txt")
    # Hexagonal(a=3.21, c=5.21, directory=output_dir, number=3, filename="Ti_XRD.txt")
    # Orthorhombic(a=5.43, b=6.21, c=7.05, directory=output_dir, number=3, filename="Ortho_XRD.txt")
    # Monoclinic(a=5.43, b=6.21, c=7.05, beta_deg=110.5, directory=output_dir, number=3, filename="Mono_XRD.txt")
    # Triclinic(a=5.0, b=6.0, c=7.0, alpha_deg=80, beta_deg=85, gamma_deg=95, directory=output_dir, number=2, filename="Tri_XRD.txt")
```
It is made for the most optimal use for the user. First it is needed to specify the output directory using the address of such file. After that, it depends on what Bravaise lattice is needed. They are callable functions using the name of the lattice. After that you need to specify lattice parameters of the unit cell depending on the type of lattice, i.e. some have only a,c others can have a,b,c. If the angles are not 90°, then it is needed to specify these angles in degrees. Then there is the **number** parameter. This specifie up to which Miller index you want to calculate all the parameters, i.e. number=3 means up to (333). Then just specify the name of the .txt file and it will output it in a format as __Miller indeces, d_space, 2theta__. It is the same format as used for plotting the results in XRD plotter.

## Modified Scherrer equation calculation
Using this script, it is possible to calculate crystal size from XRD spectra from multiple peaks. As with my other codes, there is an input section at the end, where the parameters can be changed.
### Usage
```
# =============================================================================
#  Convenience entry point - run directly:  python modified_scherrer.py
#  Or paste/edit the block below into a Spyder cell and press Ctrl+Enter.
# =============================================================================

if __name__ == "__main__":

    m = ModifiedScherrer(
        xy_file            = r"C:\...\.xy",   # << your pattern file
        label              = "SnO2_RT_final",     # free text, goes into the output file names
        # ── Instrument ────────────────────────────────────────────────
        wavelength         = 0.154060,   # nm -> Cu Ka1. Cu Ka average = 0.15418
        K                  = 0.89,      # Scherrer shape factor used in the paper
        instrumental_fwhm  = 0.0,       # deg -> from a LaB6/Si standard, e.g. 0.08
        two_theta_min      = 10.0,
        two_theta_max      = 90.0,
        # ── Peak detection (run 1: every peak gets an ID, P1, P2, ...) ─
        dry_run            = False,     # << True = only detect, fit and list the
                                        #    peaks with their IDs, then stop
        prominence_frac    = 0.02,      # threshold as a fraction of max intensity
        min_distance_deg   = 3,      # deg -> minimum peak separation Recommended value = 0.3
        # ── Which peaks to use (run 2) ────────────────────────────────
        #   MANUAL : use_peaks = ["P10", "P23", "P28", "P34", "P38", "P40", "P42"]
        #            (IDs come from the dry run; plain numbers like [10, 23] work too)
        #   AUTO   : use_peaks = None -> take the cleanly fitted peaks, strongest
        #            first, limited by min_intensity and n_peaks below
        use_peaks          = None,
        #use_peaks          = ["P6", "P7", "P12", "P13", "P14"],
        exclude_peaks      = [],        # IDs to drop from whatever was selected
        lock_peaks         = [],        # IDs the outlier pruning may never remove
        n_peaks            = 12,        # AUTO only: keep the N most intense
        min_intensity      = None,      # AUTO only: net-height cutoff in counts None
        # ── Profile fitting ───────────────────────────────────────────
        profile            = "pseudo_voigt",  # "pseudo_voigt"|"gaussian"|"lorentzian"
        fit_window_factor  = 3.0,       # window half width = factor * rough FWHM, Recommended value = 3.0
        min_fit_r2         = 0.2,      # flags bad profile fits. 0 = accept everything, Recommended value = 0.8
        # ── Modified Scherrer rules ───────────────────────────────────
        prune_outliers     = True,    # False = fit exactly the peaks you gave
        #prune_outliers     = False,
        min_peaks_kept     = 5,         # never prune below this many peaks
        slope_tolerance    = 0.15,      # stop pruning once |slope - 1| < this
        paper_rad_factor   = False,     # True reproduces the paper's rounded 0.0174
        # ── Output ────────────────────────────────────────────────────
        output_dir         = r"C:\...",      # folder for report .txt, .csv and .png
        # Choose any combination of the three plot types, or None to skip.
        #   "pattern"  – measured pattern with every peak marked and labelled
        #   "fits"     – the profile fits, so you can check each FWHM
        #   "scherrer" – the Ln beta vs Ln(1/cos theta) plot
        plot = ["pattern", "scherrer", "fits"],
        verbose            = True,
    )

    res = m.run()
    ```
Firstly, the address for the .xy file from XRD must be changed in **xy_file** parameters and the address of the output directory, where it will put the graphs and results in **output_dir** parameter.
There are several sections, that can be changed. If the spectra is measured at different machine than it is at FZU, you will need to change the section **Instrument**, otherwise it is setup for our machine. Section **Peak detection** can be usefull, as it can firstly look at the measured spectra, identify and fit the peaks, and output the list of the peaks. This can be good for optimizing the parameters such as **min_distance_deg, min_fit_r2, min_intensity, etc.** For normal output the **dry_run** shall be set as **False**, otherwise, if you want the optimatization process set it as **True**.
Then there is the main calculation. It can be set as automatic, i.e. you just set the adresses of the files and it does everything for you and outputs the value of crystal size from scherrer formula. For this mode the parameter **use_peaks** must be set as **None**. Sometimes there might be a problem, that the software uses some peaks, that are unwanted or you have two phases of material in you sample. That is why the **Manual** mode was added. For that, you first need the IDs of the peaks from dry_run or first automatic run. In the **use_peaks** parameter you input the list of the peaks that should be considered for the calculation as **["P6", "P7", "P12", "P13", "P14"]**. The optimatization proccess relies on the pruning of the outliers, this means, that it will try to not count peaks at higher degrees, which can skew results. If you want to use this optimatization (which is recommended), the parameter **prune_outliers** as **True**. Turn it **False** only if you want to fit the manually selected peaks.
The usage is quite easy, when the operator gets used to, which parameter changes what, it can be made used on samples which have quite difficult XRD spectra with several phases of different materials.
