# Van-der-Pauw-measurement
Python code for operating  Keithley 6487 and Keithley 6517B for four-point Van der Pauw resistivity measurement.
This code has such a structure, that you need to open it using any IDE, such as Spyder, Jupyter Notebook, Visual stuio etc. After opening this document the lines, that need to be changed for parameters specification are at the end of the code. I will now explain, what each row does.
## Changeable code in the file
```
if __name__ == "__main__":
    m = ResistivityMeasurement(
        k6487_resource     = "GPIB0::22::INSTR",   # << adjust GPIB address
        k6517b_resource    = "GPIB0::27::INSTR",   # << adjust GPIB address
        voltage_list       = [-500, -200, -100, 100, 200 , 500],  # V
        #voltage_list       = [-50, -20,-10, 10, 20, 50],  # V
        #voltage_list       = [-5, -2,-1, 1, 2, 5],  # V
        n_samples          = 500,
        sample_interval    = 0.05,      # s  ->  ~100 Hz acquisition rate, sample interval must be shorter than nplc
        nplc               = 1,         # 1 PLC = 16.7 ms @ 60 Hz
        current_compliance = 2e-3,      # A  ->  1 mA over-current limit
        #current_compliance = 20e-3,      # A  ->  1 mA over-current limit
        voltage_range      = 500,      # V  ->  10 V source range on 6487
        #voltage_range      = 10,      # V  ->  10 V source range on 6487
        volt_meter_range   = 200,      # V  ->  10 V range on 6517B
        volt_meter_auto    = True,
        guard_enabled      = True,      # enables SYST:GUAR ON on 6517B
        settling_time      = 60,       # s  ->  wait after source enable
        output_dir         = r"C:...",       # folder for output .txt files
        # ── Plotting ──────────────────────────────────────────────────
        # Choose any combination of the three plot types, or set to None
        # to skip plotting entirely.
        #   "I_t"  – current vs time  (one subplot per voltage step)
        #   "V_t"  – voltage vs time  (one subplot per voltage step)
        #   "I_V"  – current vs voltage (all steps overlaid)
        plot = ["I_t"],  # << remove unwanted types or set to None
    )
    m.run()
```
I will now go through the individual commands and what they change.
```
k6487_resource     = "GPIB0::22::INSTR",   # << adjust GPIB address
k6517b_resource    = "GPIB0::27::INSTR",   # << adjust GPIB address
```
This is the definition of the adresses of the devices, they should be the same. If not, they can be changed in the menus of the devices or copy the new adresses from **Connection expert**.
```
voltage_list       = [-500, -200, -100, 100, 200 , 500],  # V
#voltage_list       = [-50, -20,-10, 10, 20, 50],  # V
#voltage_list       = [-5, -2,-1, 1, 2, 5],  # V
```
Here you input the voltages you want to measure on your samples. It is quite handy to have several lists prepared and only uncomment the one, you want to use as the behaviour of the samples can differ a lot. The code will go through this list as is written, i.e. from left to right, it does not sort it from lowest to highest voltages.
```
n_samples          = 500,
sample_interval    = 0.05,      # s  ->  ~100 Hz acquisition rate, sample interval must be shorter than nplc
nplc               = 1,         # 1 PLC = 16.7 ms @ 60 Hz
```
The other main parameters are the number of samples taken for one measurement and time interval between each measured point. The **n_samples** values depends on the size of the buffers of the devices. For this configuration the maximum number of points should be **3000** but it is advised to have between **0-2000**. The **sample_interval** is the time between measurement of two points, it should somehow correspond with nplc, which should be: "determines how long the instrument's analog-to-digital converter integrates a signal for a single reading", therefore it should have some relation to sample_interval but I did not understand the exact calculation between these two to have some impact for the devices to work properly. Therefore it is good to keep the **nplc=1** and change only **sample_interval** which, for this nplc value, can have the minimal value of 0.02 s up to any number. Probably the measurement for one voltage value should not be too long as the devices have some timeout value set. If it is exceeded it will output error.
```
current_compliance = 2e-3,      # A  ->  2 mA over-current limit
#current_compliance = 20e-3,      # A  ->  20 mA over-current limit
voltage_range      = 500,      # V  ->  10 V source range on 6487
#voltage_range      = 10,      # V  ->  10 V source range on 6487
volt_meter_range   = 200,      # V  ->  10 V range on 6517B
volt_meter_auto    = True,  
```
These commands controls the setting of the devices. **current_compliance and voltage_range** are setting for Keithley 6487 and **volt_meter_range and volt_meter_auto** are for Keithley 6517B. 
Current compliance is the highest current measureable before the device has to lower the applied voltage internally as not to damage the device, i.e. if you set the voltage to be +100V and it will go over the current limit of 2 mA, it will internally lower the voltage to lower value, but it will still show you, that +100V are applied, eventhough it is not. The Keithley 6487 has two setting for current compliance. Fot the voltage from -500V to +500V it is only 2 mA, for voltages from -10V to +10V it can measure up to 20mA. For the **voltage_range** accepted values are 10, 50 and 500V, this setting will also change the number of decimal points available for the voltage list setting.. This is where the operator needs to watch out which of these values the input. If you input **voltage_range** higher than 10, the current compliance will be strictly set to 2 mA, even if you try to set it higher with the command. For the higher current compliance to be available, the voltage range must be set to 10V.
The setting for Keithley 6517B are the ranges for the measuremnt of the voltage across the sample. Either it can be set automatically having **volt_meter_auto** set as True or it can be set as a hard limit on one number, ususally this setting is not changed.
```
guard_enabled      = True,      # enables SYST:GUAR ON on 6517B
settling_time      = 60,       # s  ->  wait after source enable
output_dir         = r"C:...",       # folder for output .txt files  
```
These commands are complementary, where you specify some things. When voltage is measured using Keithley 6517B, the guard should be enabled, this will serve as protection and proper way to measure the voltage. **Settling_time** is wait time of the first point taken and apllying the voltage, i.e. if it is set to 60s, it means that after it applies the voltage from voltage list it will wait 60 seconds before starting the measurement, this can help with som non-linear effects, instabilities of the voltage source in the beggining or draining the current carriers created by light when installing the sample on the holder. The **output_dir** is the adress where the measured characteristics in .txt format will be saved. The folders does not need to be created beforehand, inputting the adress it will create this route, if some folders are missing and then output the files named using the voltages from voltage_list in to these folders.
```
# ── Plotting ──────────────────────────────────────────────────
        # Choose any combination of the three plot types, or set to None
        # to skip plotting entirely.
        #   "I_t"  – current vs time  (one subplot per voltage step)
        #   "V_t"  – voltage vs time  (one subplot per voltage step)
        #   "I_V"  – current vs voltage (all steps overlaid)
        plot = ["I_t"],  # << remove unwanted types or set to None
```
This function should be able to plot the measured characteristics using these different parameters. It has some problem now, so it does not create these graphs and I need to repair it. So it might be good idea to have it set on **None** not to get error after measurement.
