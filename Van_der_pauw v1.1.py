# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 15:22:21 2026

@author: tmase
"""

"""
resistivity_measurement.py
===========================
Four-point resistivity measurement using:
  - Keithley 6487  : Voltage source + current meter
  - Keithley 6517B : Voltage meter  (Guard terminal supported)

HOW TO USE IN SPYDER (or any IDE / interactive console)
--------------------------------------------------------

  -- Minimal (uses all defaults): ----------------------------------------

    from resistivity_measurement import ResistivityMeasurement
    m = ResistivityMeasurement()
    m.run()

  -- Full configuration in a single constructor call: --------------------

    from resistivity_measurement import ResistivityMeasurement
    m = ResistivityMeasurement(
        k6487_resource     = "GPIB0::22::INSTR",
        k6517b_resource    = "GPIB0::27::INSTR",
        voltage_list       = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
        n_samples          = 1000,
        sample_interval    = 0.01,
        nplc               = 1,
        current_compliance = 1e-3,
        voltage_range      = 10.0,
        volt_meter_range   = 10.0,
        volt_meter_auto    = False,
        guard_enabled      = True,
        settling_time      = 0.2,
        output_dir         = r"C:/Data/Measurements",
    )
    m.run()

  -- Quick sweep with numpy linspace: ------------------------------------

    import numpy as np
    from resistivity_measurement import ResistivityMeasurement
    m = ResistivityMeasurement(voltage_list=np.linspace(0.1, 10, 20).tolist())
    m.run()

Dependencies:  pip install pyvisa pyvisa-py numpy
               NI-VISA (or compatible backend) required for GPIB.
"""

import pyvisa
import time
import os
import datetime
import numpy as np
import re
import matplotlib.pyplot as plt


# =============================================================================
#  ResistivityMeasurement class
# =============================================================================

class ResistivityMeasurement:
    """
    Encapsulates a four-point resistivity measurement sweep.

    Parameters
    ----------
    k6487_resource : str
        VISA resource string for the Keithley 6487 (voltage source / ammeter).
        Default: "GPIB0::22::INSTR"
    k6517b_resource : str
        VISA resource string for the Keithley 6517B (voltmeter).
        Default: "GPIB0::27::INSTR"
    voltage_list : list of float
        Sequence of source voltages [V] to step through.
        Each entry produces one output .txt file with n_samples readings.
        Default: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    n_samples : int
        Number of (I, V) paired readings collected per voltage step.
        Default: 1000
    sample_interval : float
        Target time [s] between successive readings.
        Default: 0.01  (100 Hz)
    nplc : float
        Integration time in power-line cycles for the 6487.
        Default: 1
    current_compliance : float
        Current compliance [A] on the 6487.
        Default: 1e-3
    voltage_range : float
        Source voltage range on the 6487 (10.0 or 50.0 V).
        Default: 10.0
    volt_meter_range : float
        Measurement range [V] on the 6517B (used when volt_meter_auto=False).
        Default: 10.0
    volt_meter_auto : bool
        Enable auto-range on the 6517B voltmeter.
        Default: False
    guard_enabled : bool
        If True, sends SENS:VOLT:DC:GUAR ON to the 6517B.
        Default: True
    settling_time : float
        Seconds to wait after enabling the source before sampling.
        Default: 0.2
    output_dir : str
        Directory where .txt result files are written.
        Default: "."
    """

    _DEFAULTS = dict(
        k6487_resource     = "GPIB0::22::INSTR",
        k6517b_resource    = "GPIB0::27::INSTR",
        voltage_list       = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
        n_samples          = 1000,
        sample_interval    = 0.01,
        nplc               = 1,
        current_compliance = 1e-3,
        voltage_range      = 10.0,
        volt_meter_range   = 10.0,
        volt_meter_auto    = False,
        guard_enabled      = True,
        settling_time      = 0.2,
        output_dir         = ".",
        plot               = None,
    )

    def __init__(self, **kwargs):
        cfg = {**self._DEFAULTS, **kwargs}

        self.k6487_resource     = cfg["k6487_resource"]
        self.k6517b_resource    = cfg["k6517b_resource"]
        self.voltage_list       = list(cfg["voltage_list"])
        self.n_samples          = int(cfg["n_samples"])
        self.sample_interval    = float(cfg["sample_interval"])
        self.nplc               = float(cfg["nplc"])
        self.current_compliance = float(cfg["current_compliance"])
        self.voltage_range      = float(cfg["voltage_range"])
        self.volt_meter_range   = float(cfg["volt_meter_range"])
        self.volt_meter_auto    = bool(cfg["volt_meter_auto"])
        self.guard_enabled      = bool(cfg["guard_enabled"])
        self.settling_time      = float(cfg["settling_time"])
        self.output_dir         = cfg["output_dir"]
        self.plot               = list(cfg["plot"]) if cfg["plot"] else []

        self._rm     = None
        self._k6487  = None
        self._k6517b = None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self):
        """Execute the full measurement sweep and save results to disk."""
        self._print_banner()
        os.makedirs(self.output_dir, exist_ok=True)

        self._rm = pyvisa.ResourceManager()
        try:
            self._connect()
            self._identify()
            
            self._configure_k6487()
            self._configure_k6517b()
            saved = self._sweep()
            self._safe_off()

            print("\n" + "=" * 60)
            print("  Measurement complete.")
            print(f"  {len(saved)} file(s) saved to: "
                  f"{os.path.abspath(self.output_dir)}")
            for f in saved:
                print(f"    {os.path.basename(f)}")
            print("=" * 60)

        except pyvisa.errors.VisaIOError as exc:
            print(f"\n[ERROR] VISA communication error:\n  {exc}")
            raise
        finally:
            self._safe_off()
            if self._rm:
                self._rm.close()
            print("Connections closed.")

    # ------------------------------------------------------------------
    # Connection  (no *RST sent to either instrument)
    # ------------------------------------------------------------------

    def _connect(self):
        print("\n[1] Opening instrument connections ...")

        print(f"    Keithley 6487  -> {self.k6487_resource}")
        self._k6487 = self._rm.open_resource(self.k6487_resource)
        self._k6487.timeout           = 10_000   # ms
        self._k6487.write_termination = "\n"
        self._k6487.read_termination  = "\n"

        print(f"    Keithley 6517B -> {self.k6517b_resource}")
        self._k6517b = self._rm.open_resource(self.k6517b_resource)
        self._k6517b.timeout           = 10_000   # ms
        self._k6517b.write_termination = "\n"
        self._k6517b.read_termination  = "\n"

    def _identify(self):
        """Clear error queue on 6487 and identify both instruments."""
        print("\n[2] Identifying instruments (no reset) ...")
        # *CLS clears the status registers and error queue only – no settings changed
        self._k6487.write("*CLS")
        idn_6487  = self._k6487.query("*IDN?").strip()
        idn_6517b = self._k6517b.query("*IDN?").strip()
        print(f"    [K6487 ] {idn_6487}")
        print(f"    [K6517B] {idn_6517b}")

    # ------------------------------------------------------------------
    # Instrument configuration
    # ------------------------------------------------------------------

    def _configure_k6487(self):
        """
        Configure the 6487 voltage source and current measurement.
        No reset is sent. Zero-check is left exactly as the operator
        set it on the front panel before running.
        """
        print("\n[3] Configuring Keithley 6487 ...")
        k = self._k6487
        k.write("*RST")
        time.sleep(1.0)           # wait for reset to complete
        k.write("SYST:ZCH OFF") # disconnect zero-check relay
        time.sleep(0.5)           # allow input relay to physically close
        # Voltage source
        k.write(f"SOUR:VOLT:RANG {self.voltage_range}")
        k.write("SOUR:VOLT 0")
        k.write(f"SOUR:VOLT:ILIM {self.current_compliance:.3E}")
        k.write("SOUR:VOLT:STAT OFF")

        # Current measurement
        k.write("SENS:FUNC 'CURR'")
        k.write("SENS:CURR:RANG:AUTO ON")
        k.write(f"SENS:CURR:NPLC {self.nplc}")
        
        k.write("INIT:CONT OFF")   # stop continuous buffering
        k.write("TRIG:SOUR IMM")   # trigger immediately on each call
        k.write("TRIG:COUN 1")     # one reading per call
        k.write("TRAC:CLE")        # clear any pre-run buffered samples

        print("    6487 configured.")

    def _configure_k6517b(self):
        """
        The 6517B is used as prepared from power-on.
        Only the Guard terminal state is set here.
        """
        print("\n[4] Keithley 6517B – setting Guard terminal only ...")
        k = self._k6517b

        if self.guard_enabled:
            k.write("SENS:VOLT:DC:GUAR ON")
            print("    Guard terminal : ON  (SENS:VOLT:DC:GUAR ON)")
        else:
            k.write("SENS:VOLT:DC:GUAR OFF")
            print("    Guard terminal : OFF")

        print("    6517B ready.")

    # ------------------------------------------------------------------
    # Measurement sweep
    # ------------------------------------------------------------------

    def _sweep(self) -> list:
        n = len(self.voltage_list)
        print(f"\n[5] Starting sweep: {n} voltage step(s) ...")
        saved_files = []
        all_data    = []

        for idx, voltage in enumerate(self.voltage_list, start=1):
            print(f"\n  -- Step {idx}/{n}: V_set = {voltage:+.4f} V --")
            data  = self._measure_step(voltage)
            fname = self._save(data, voltage, idx)
            saved_files.append(fname)
            all_data.append(data)
            print(f"     R_mean = {data['R_mean']:.4E} Ohm  "
                  f"(+/- {data['R_std']:.2E} Ohm)")

        return saved_files, all_data

    def _measure_step(self, voltage: float) -> dict:
        """Apply voltage and collect n_samples synchronized (I, V) pairs."""
        k6487  = self._k6487
        k6517b = self._k6517b

        k6487.write(f"SOUR:VOLT {voltage:.6E}")
        k6487.write("SOUR:VOLT:STAT ON")
        time.sleep(self.settling_time)
        k6487.write("TRAC:CLE")    # discard samples taken before/during settling
        time.sleep(1.0)           # wait for reset to complete
        k6487.write("SYST:ZCH OFF") # disconnect zero-check relay
        time.sleep(0.5)           # allow input relay to physically close
        currents = np.empty(self.n_samples)
        voltages  = np.empty(self.n_samples)

        for i in range(self.n_samples):
            t_start = time.perf_counter()

            currents[i] = self._read_current()
            voltages[i]  = self._read_voltage()

            if (i + 1) % 100 == 0:
                I_disp = f"{currents[i]:.4E}" if not np.isnan(currents[i]) else "OVERRANGE"
                V_disp = f"{voltages[i]:.4E}" if not np.isnan(voltages[i]) else "OVERRANGE"
                print(f"    Sample {i+1:4d}/{self.n_samples}  "
                      f"I = {I_disp} A   V = {V_disp} V")

            elapsed = time.perf_counter() - t_start
            wait    = self.sample_interval - elapsed
            if wait > 0:
                time.sleep(wait)

        k6487.write("SOUR:VOLT:STAT OFF")
        time.sleep(0.1)

        resistance = voltages / currents

        nan_I = int(np.sum(np.isnan(currents)))
        nan_V = int(np.sum(np.isnan(voltages)))
        if nan_I or nan_V:
            print(f"    [WARNING] Overrange samples: I={nan_I}, V={nan_V}")

        return {
            "set_voltage" : voltage,
            "currents"    : currents,
            "voltages"    : voltages,
            "resistance"  : resistance,
            "nan_I"       : nan_I,
            "nan_V"       : nan_V,
            "I_mean"      : float(np.nanmean(currents)),
            "I_std"       : float(np.nanstd(currents)),
            "V_mean"      : float(np.nanmean(voltages)),
            "V_std"       : float(np.nanstd(voltages)),
            "R_mean"      : float(np.nanmean(resistance)),
            "R_std"       : float(np.nanstd(resistance)),
        }

    # ------------------------------------------------------------------
    # Single-reading helpers
    # ------------------------------------------------------------------

    # 6517B trailing status characters:
    #   N = Normal   O = Overflow   Z = Overrange   U = Underrange   H/L = Limit
    _OVERFLOW_FLAGS = frozenset("ZOUH")

    @staticmethod
    def _extract_number(field: str, overflow_flags: frozenset) -> float:
        """
        Parse a float from a Keithley SCPI reading field that may carry a
        trailing unit string and/or single-character status flag, e.g.:
            '+1.23456E-06A'      (6487 current)
            '+9.87654E-01VDCN'   (6517B normal)
            '+9.91000E+37VDCZ'   (6517B overrange -> NaN)
        """
        field = field.strip()
        m = re.match(r'([+-]?\d+\.?\d*(?:[Ee][+-]?\d+)?)', field)
        if not m:
            raise ValueError(f"No numeric value in SCPI field: {field!r}")

        numeric_str = m.group(1)
        remainder   = field[m.end():].upper()

        for unit in ("VDC", "VAC", "OHM", "AMP", "A", "V"):
            remainder = remainder.replace(unit, "")

        if any(ch in overflow_flags for ch in remainder):
            return float("nan")

        return float(numeric_str)

    def _read_current(self) -> float:
        """
        Read one current sample from the 6487 with READ?.
        Requires zero-check to be OFF on the instrument before running
        (set via the front panel: press Z-CHK until ZCHK disappears).
        Response format:  +1.23456E-06A,+1.00000E+00V,+0
        """
        #self._k6487.write("SYST:ZCHE OFF") # disconnect zero-check relay
        raw   = self._k6487.query("READ?").strip()
        field = raw.split(",")[0]
        return self._extract_number(field, self._OVERFLOW_FLAGS)

    def _read_voltage(self) -> float:
        """
        Read one voltage sample from the 6517B with READ?.
        Response format:  +9.87654E-01VDCN,+1.234E+03,+0
        """
        raw   = self._k6517b.query("READ?").strip()
        field = raw.split(",")[0]
        value = self._extract_number(field, self._OVERFLOW_FLAGS)
        if np.isnan(value):
            print(f"    [WARNING] 6517B overrange: {raw!r} -> NaN")
        return value

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------

    def _save(self, data: dict, voltage: float, idx: int) -> str:
        ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(
            self.output_dir,
            f"resistivity_{ts}_step{idx:03d}_{voltage:+.4f}V.txt"
        )

        header = "\n".join([
            "# Four-Point Resistivity Measurement",
            f"# Date/Time           : {datetime.datetime.now().isoformat()}",
            f"# K6487  resource     : {self.k6487_resource}",
            f"# K6517B resource     : {self.k6517b_resource}",
            f"# Guard (6517B)       : {'ON' if self.guard_enabled else 'OFF'}",
            f"# Set Voltage (V)     : {voltage:.6E}",
            f"# N Samples           : {self.n_samples}",
            f"# Sample interval (s) : {self.sample_interval}",
            f"# NPLC                : {self.nplc}",
            f"# I_compliance (A)    : {self.current_compliance:.3E}",
            f"# I_mean (A)          : {data['I_mean']:.6E}",
            f"# I_std  (A)          : {data['I_std']:.6E}",
            f"# V_mean (V)          : {data['V_mean']:.6E}",
            f"# V_std  (V)          : {data['V_std']:.6E}",
            f"# R_mean (Ohm)        : {data['R_mean']:.6E}",
            f"# R_std  (Ohm)        : {data['R_std']:.6E}",
            f"# Overrange I samples : {data['nan_I']}",
            f"# Overrange V samples : {data['nan_V']}",
            "#",
            "# index\tCurrent_A\tVoltage_V\tResistance_Ohm",
        ])

        def fmt(x):
            return f"{x:.8E}" if not np.isnan(x) else "NaN"

        with open(fname, "w") as f:
            f.write(header + "\n")
            for i, (I, V, R) in enumerate(
                zip(data["currents"], data["voltages"], data["resistance"])
            ):
                f.write(f"{i}\t{fmt(I)}\t{fmt(V)}\t{fmt(R)}\n")

        print(f"    Saved -> {fname}")
        return fname

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def _plot_results(self, all_data: list):
        """
        Plot results after the sweep based on the self.plot list.
        Options:
            "I_t"  – current vs time, one subplot per voltage step
            "V_t"  – voltage vs time, one subplot per voltage step
            "I_V"  – current vs voltage, all steps overlaid on one axes
        """
        valid = {"I_t", "V_t", "I_V"}
        requested = [p.strip() for p in self.plot]
        unknown = [p for p in requested if p not in valid]
        if unknown:
            print(f"  [WARNING] Unknown plot type(s) ignored: {unknown}")
        requested = [p for p in requested if p in valid]
        if not requested:
            return
 
        n_steps = len(all_data)
 
        for plot_type in requested:
 
            # ── I(t) and V(t) : one subplot per voltage step ──────────
            if plot_type in ("I_t", "V_t"):
                ncols = min(3, n_steps)
                nrows = (n_steps + ncols - 1) // ncols
                fig, axes = plt.subplots(nrows, ncols,
                                         figsize=(5 * ncols, 4 * nrows),
                                         squeeze=False)
                fig.suptitle(
                    "Current vs Time" if plot_type == "I_t" else "Voltage vs Time",
                    fontsize=14, fontweight="bold"
                )
 
                for idx, data in enumerate(all_data):
                    ax  = axes[idx // ncols][idx % ncols]
                    t   = np.arange(self.n_samples) * self.sample_interval
 
                    if plot_type == "I_t":
                        y      = data["currents"]
                        ylabel = "Current (A)"
                        color  = "tab:blue"
                    else:
                        y      = data["voltages"]
                        ylabel = "Voltage (V)"
                        color  = "tab:orange"
 
                    ax.plot(t, y, color=color, linewidth=0.8)
                    ax.set_title(f"V_set = {data['set_voltage']:+.2f} V")
                    ax.set_xlabel("Time (s)")
                    ax.set_ylabel(ylabel)
                    ax.grid(True, linestyle="--", alpha=0.5)
 
                # Hide unused subplots
                for idx in range(n_steps, nrows * ncols):
                    axes[idx // ncols][idx % ncols].set_visible(False)
 
                fig.tight_layout()
                plt.show()
 
            # ── I(V) : all steps overlaid ─────────────────────────────
            elif plot_type == "I_V":
                fig, ax = plt.subplots(figsize=(7, 5))
                fig.suptitle("Current vs Voltage", fontsize=14, fontweight="bold")
 
                for data in all_data:
                    v_set = data["set_voltage"]
                    # Use mean voltage measured by 6517B as x-axis
                    ax.scatter(data["voltages"], data["currents"],
                               s=4, label=f"V_set={v_set:+.1f} V", alpha=0.7)
 
                ax.set_xlabel("Measured Voltage (V)")
                ax.set_ylabel("Measured Current (A)")
                ax.legend(fontsize=8, loc="best")
                ax.grid(True, linestyle="--", alpha=0.5)
                fig.tight_layout()
                plt.show()
                
                
    # ------------------------------------------------------------------
    # Safety
    # ------------------------------------------------------------------

    def _safe_off(self):
        """Zero and disable the 6487 source. 6517B is not touched."""
        try:
            if self._k6487:
                self._k6487.write("SOUR:VOLT 0")
                self._k6487.write("SOUR:VOLT:STAT OFF")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Banner
    # ------------------------------------------------------------------

    def _print_banner(self):
        print("=" * 60)
        print("  Four-Point Resistivity Measurement")
        print("=" * 60)
        print(f"  6487  resource   : {self.k6487_resource}")
        print(f"  6517B resource   : {self.k6517b_resource}")
        print(f"  Voltage steps    : {self.voltage_list}")
        print(f"  Samples / step   : {self.n_samples}")
        print(f"  Sample interval  : {self.sample_interval} s")
        print(f"  NPLC             : {self.nplc}")
        print(f"  Compliance       : {self.current_compliance:.2E} A")
        print(f"  Guard (6517B)    : {'ON' if self.guard_enabled else 'OFF'}")
        print(f"  Output dir       : {os.path.abspath(self.output_dir)}")
        print("=" * 60)



# =============================================================================
#  Convenience entry point – run directly:  python resistivity_measurement.py
#  Or paste/edit the block below into a Spyder cell and press Ctrl+Enter.
# =============================================================================

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
        output_dir         = r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\PN_Junc\SnO-SnO2\Rofaida\271125\Lightr_A",       # folder for output .txt files
        # ── Plotting ──────────────────────────────────────────────────
        # Choose any combination of the three plot types, or set to None
        # to skip plotting entirely.
        #   "I_t"  – current vs time  (one subplot per voltage step)
        #   "V_t"  – voltage vs time  (one subplot per voltage step)
        #   "I_V"  – current vs voltage (all steps overlaid)
        plot = ["I_t"],  # << remove unwanted types or set to None
    )

    m.run()