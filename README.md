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
With these lines the setting of the instrument can be changed. Firstly, we have the voltage list, which can have values from -500V to +500V. This creates a list of voltages, which will be applied on the device during the measurement. These also have some limitations with the next parameters. The _nplc_ setting is the same as for the Van der Pauw measurement and should not be changed, unless is fully understood and correctly calculated as it can easily stop the measuring device working correctly. The _current_compliance_ and _voltage_range_ are the main parameters to change as they affect the modes in which the device can measure. There are two main modes. First is, when the voltage range is set to 10 V, which then allows to have the maximum measureable current up to 20 mA (2.0e-2). With this setting the voltage list can have only values from -10V to +10V. The socond mode, which is mostly used is when the voltage limit is 500V. With this setting, the maximum current is only 2.5 mA (2.5e-3). Even if you try to set the current compliance to 20 mA and the voltage range to 500V, it will not work, as the voltage range overrides the maximum possible measureable current. The last parameter is _settling_time_, which is the time the device waits after outputing the voltage for the first measured point to be taken. This parameters is in second and the correct value is highly dependent on the properties of the film. If the semiconducting film takes a long time to dim out after illumination, this can go up to minutes, as this is mainly the time between measurements of the different voltages.
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
The Phase 2 is the most important as in this phase we will measure all of the wanted effect. It is classified as fast, due to very short intervals, these can be as short as 0.02s. With the example as in the code above, we have 250 fast point before illumination, then we turn on the illumination for 500 fast points, which is 25s. During this, we can measure the effect of illumination, how fast the semiconductor is and other parameters. After point 750 in the fast phase, we turn off the illumination and in the next 250 points we measure how fast dims out the semiconductor. As most of these are quite fast, the current usually falls by an order of magnitude in tens of points or even less. Depending on the effect we want to observe, these times can be changed. Some semiconductor mighnt not saturate their current under illumination under 25 seconds, therefore we will not be able to observe this maximum value. One solution is to prolong the Phase interval, which would help with it but at a cost of smaller resolution after turning off the illumination. One must decide, what is more important to them.
The Phase 3 is longterm observation of the semiconductor after illumination. This is set similarly as Phase 1.
### Output
```
# ── Output ──────────────────────────────────────────────────────────
        output_dir          = r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\PN_Junc\TiO2\DC-MAG\TiO2_068_SAP_A\Dark_bef",
        plot                = ["I_t", "I_log"],
```
Again, we must specify the output directory, where the measured data will be exported to in .txt files. There is also an option for plotting the measured data after measurement. This is quite usefull for first evaluation if anything needs to be remeasured.
