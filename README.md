# Response of semiconductors on light
This script is used for measuring the speed of the semiconductor, when illuminated by UV light and after illumination when under voltage. Same with other scripts for Keithley devices, the only part to be changed is at the end of the script. Compared to Van der Pauw measurement, this only uses Keithley 6487. 
## Functions
At the end of the code, the only parameters needed to be changed are in **m = CurrentMonitor(...**, I have prepared there two premade measurements, one is normal measurement, where you have three parts, which will be explained further. And the other one, which is commented is for the measurement of dark current of the semiconductor before illumination. Below is the whole section with parameters, that can be changed. I will now discuss their meaning.
```
m = CurrentMonitor(
        k6487_resource              = "GPIB0::22::INSTR",  # << adjust

        # Voltage steps – one file per voltage
        voltage_list                = [10, 50, 100],  # V

        # Phase 1 – slow baseline before the burst
        n_slow_pre                  = 500,
        slow_pre_mode               = "constant",
        slow_pre_interval           = 1.0,                  # 5 s between pts

        # Phase 2 – dense transient capture
        n_fast                      = 1000,
        fast_interval               = 0.05,                 # 50 ms -> 20 Hz

        # Phase 3 – long-term monitoring after burst
        n_slow_post                 = 500,
        slow_post_mode              = "constant",
        slow_post_interval          = 1.0,                  # 5 s between pts

        # Instrument
        nplc                        = 1,
        current_compliance          = 2.5e-2,
        voltage_range               = 500.0,
        settling_time               = 60.0,

        # ── Output ──────────────────────────────────────────────────────────
        output_dir          = r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\PN_Junc\TiO2\DC-MAG\TiO2_068_SAP_A",
        plot                = ["I_t", "I_log"],
    )
```
### Instrument settings
```
# Voltage steps – one file per voltage
 voltage_list                = [10, 50, 100],  # V
...
# Instrument
        nplc                        = 1,
        current_compliance          = 2.5e-3,
        voltage_range               = 500.0,
        settling_time               = 60.0,

```
With these lines the setting of the instrument can be changed. Firstly, we have the voltage list, which can have values from -500V to +500V. This creates a list of voltages, which will be applied on the device during the measurement. These also have some limitations with the next parameters. The _nplc_ setting is the same as for the Van der Pauw measurement and should not be changed, unless is fully understood and correctly calculated as it can easily stop the measuring device working correctly. The _current_compliance_ and _voltage_range_ are the main parameters to change as they affect the modes in which the device can measure. There are two main modes. First is, when the voltage range is set to 10 V, which then allows to have the maximum measureable current up to 20 mA (2.0e-2). With this setting the voltage list can have only values from -10V to +10V. The socond mode, which is mostly used is when the voltage limit is 500V. With this setting, the maximum current is only 2.5 mA (2.5e-3). Even if you try to set the current compliance to 20 mA and the voltage range to 500V, it will not work, as the voltage range overrides the maximum possible measureable current. The last parameter is _settling_time_, which is the time the device waits after outputing the voltage for the first measured point to be taken. This parameters is in second and the correct value is highly dependent on the properties of the film. If the semiconducting film takes a long time to decay after illumination, this can go up to minutes, as this is mainly the time between measurements of the different voltages.
### Measurement process
```
        # Phase 1 – slow baseline before the burst
        n_slow_pre                  = 500,
        slow_pre_mode               = "constant",
        slow_pre_interval           = 1.0,                  # 5 s between pts

        # Phase 2 – dense transient capture
        n_fast                      = 1000,
        fast_interval               = 0.05,                 # 50 ms -> 20 Hz

        # Phase 3 – long-term monitoring after burst
        n_slow_post                 = 500,
        slow_post_mode              = "constant",
        slow_post_interval          = 1.0,                  # 5 s between pts
```
I have created three phases of the measurement so several effects can be observed. They are labbeled as slow-fast-slow. Firstly there are few general rules. The amount of measured points for one voltage must not exceed 3000 points, as this should be the size of the buffer. If I am correct, there should not be any constraints on the time preriod of one measurement, it should prolong the timeout on the device depending on the total time set for one measurement. 
As for the slow measurement, there are two modes. The classical is **Constant**, which means, that all points are equidistant. It is set by the _interval_ setting. Second mode is **Linear**, which lineary prolongs the time between each point. For this option the start time of the interval and end time of the interval must be set. Depending on the amount of the points, the time between each point is then modified accordingly. This type of measurement is showcased at the end of the code as **Example #2**.
The measurement process is quite easy. First it is needed to measure all of the voltage before first illumination. This gives us the dark current of this film. As some of the films take a long time to get back to their dark current state, it is quite usefull to know the level. This is usually quite fast, as it takes only about 200-300 points to create a good statistic to take the level as a mean. After that the sample is preapared for the main measurement. The _Phase 1_ is there to get the dark level after illumination from previous voltage. Therefore, for slow semiconductors, this phase should be quite long, to get to the dark currents measured in the beggining. As it is not always the best option to measure for that long time, due to effectivity, it is usually sufficient to have cca 500 points with one second interval. This way we get quite a good statistics for future evaluation. 
The Phase 2 is the most important as in this phase we will measure all of the wanted effect. It is classified as fast, due to very short intervals, these can be as short as 0.02s. With the example as in the code above, we have 250 fast point before illumination, then we turn on the illumination for 500 fast points, which is 25s. During this, we can measure the effect of illumination, how fast the semiconductor is and other parameters. After point 750 in the fast phase, we turn off the illumination and in the next 250 points we measure how fast the semiconductor decays. As most of these are quite fast, the current usually falls by an order of magnitude in tens of points or even less. Depending on the effect we want to observe, these times can be changed. Some semiconductor mighnt not saturate their current under illumination under 25 seconds, therefore we will not be able to observe this maximum value. One solution is to prolong the Phase interval, which would help with it but at a cost of smaller resolution after turning off the illumination. One must decide, what is more important to them.
The Phase 3 is longterm observation of the semiconductor after illumination. This is set similarly as Phase 1.
### Output
```
# ── Output ──────────────────────────────────────────────────────────
        output_dir          = r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\PN_Junc\TiO2\DC-MAG\TiO2_068_SAP_A\Dark_bef",
        plot                = ["I_t", "I_log"],
```
Again, we must specify the output directory, where the measured data will be exported to in .txt files. There is also an option for plotting the measured data after measurement. This is quite usefull for first evaluation if anything needs to be remeasured.

## Current Plotter
This script is made for the evaluation of measured characteristics using the script above. It has several functions, which can be quite usefull, such as marking of the times, it takes for the current to fall some order of magnitude and several plotting options for comparison of multiple measurements. Compared to otheer scripts, loading of the files is quite automatic. Only thing, that is needed to change is the address of root directory, i.e. where all of the measurements starts. After this is specified, the script will create a list of all .txt files with the data and assign it a number, which then can be used for specifying which measurements to plot in the same graph. Below is the entry point, which is at the end of the script. Firstly, it is needed to run it one time to create the list. When it is already created, then it is possible to run it by the command bellow.  
```
# =============================================================================
#  ── ENTRY POINT ──────────────────────────────────────────────────────────────
# =============================================================================
if __name__ == "__main__":
    # On first run the catalogue is printed automatically.
    _ensure_scanned()
    mrun([4, 18, 30, 42, 65], mode="side", decay_markers=True)
    mrun([4, 18, 30, 42, 65], mode="overlay")
    # ── Example calls (uncomment or adapt) ────────────────────────────────────

    # ---- Example calls (uncomment or adapt) ----------------------------------

    # Overlay - default, all annotations on:
    # mrun([0, 1])

    # Overlay without decay markers (cleaner for a quick look):
    # mrun([0, 1], decay_markers=False)

    # Side by side with decay markers:
    # mrun([0, 1], mode="side")

    # Side by side without decay markers:
    # mrun([0, 1], mode="side", decay_markers=False)

    # All files for one method at 10 V (dark + illuminated together):
    # idx = [f["index"] for f in _FILES
    #        if f["method"] == "DC-MAG" and f["voltage"] == 10.0]
    # mrun(idx)

    # Compare one sample across all methods at 50 V, side by side:
    # idx = [f["index"] for f in _FILES
    #        if f["sample"] == "TiO2_067_SAP" and f["voltage"] == 50.0]
    # mrun(idx, mode="side")
```
At the beggining of the script, there is a tutorial for the use of this script, therefore, I will put it here, as it will be better, than my explanation. In the directory with the scripts, there will be a folder with examples of these graphs, so one does not need to imagine, what will the graphs look like.
```
Offline plotter for .txt files produced by Current_measurement.py
(Keithley 6487 three-phase current monitor).

Directory structure assumed
---------------------------
<root>/                         e.g.  C:\\...\\TiO2
  <method>/                     e.g.  DC-MAG
    <sample>/                   e.g.  TiO2_067_SAP
      *.txt                           illuminated measurements (10 / 50 / 100 V)
      Dark_bef/
        *.txt                         dark-before measurements

HOW TO USE
----------
1.  Set ROOT_DIR to the top-level TiO2 folder.
2.  Run the script.  It will scan the whole tree and print a numbered
    catalogue of every .txt file it finds.
3.  Call mrun() with the indices (or index ranges) you want to compare.

    mrun(selection)                          <- overlay, all annotations on
    mrun(selection, mode="side")             <- side-by-side subplots
    mrun(selection, decay_markers=False)     <- hide decay-time markers

    Examples:
        mrun([0, 1, 2])                      # overlay (default)
        mrun("0-2", mode="side")             # side-by-side subplots
        mrun([0, "3-5", 10])                 # mix of indices and ranges
        mrun("all")                          # overlay every file (use with care)
        mrun([0, 1], decay_markers=False)    # no decay annotations

Plot output
-----------
Two figures are always produced per call:
  Fig 1 - Current vs Time  (linear Y axis)
  Fig 2 - Current vs Time  (logarithmic Y axis, |I| plotted)

  mode="overlay"  -> single pair of axes; each file is a different colour
  mode="side"     -> one subplot column per file; rows = linear / log

Per-file annotations (illuminated files only):
  ......  dotted horizontal line  = mean dark current (from the paired Dark_bef
            file in the selection if present, otherwise from the slow_pre phase)
  *       star marker             = peak (max absolute) current
  v       triangle-down marker    = time after peak where I drops to I_peak / 2
  s       square marker           = time after peak where I drops by 1 order of magnitude
  o       circle marker           = time after peak where I drops by 2 orders of magnitude

  If a threshold is never reached the time is shown as inf in the legend.

Dark measurement files are drawn with dashed lines.
Each file gets its own tab10 colour so overlapping traces are distinguishable.

Dependencies:  pip install numpy matplotlib
```
