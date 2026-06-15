# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 13:55:27 2026

@author: tmase
"""

# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
current_monitor_6487.py  –  v3
================================
Long-duration current monitoring using the Keithley 6487 as both
voltage source and ammeter.  No second instrument is required.

The script steps through a list of voltages and runs the full
three-phase sampling schedule at each voltage, saving one .txt file
per voltage step.

Buffer note
-----------
The Keithley 6487 internal buffer holds up to 3 000 readings.
This script reads sample-by-sample over GPIB (READ? query), so the
total sample count is limited only by time, not by memory.

Three-phase sampling schedule (applied at every voltage step)
-------------------------------------------------------------

  Phase 1 – "slow_pre"  (baseline before stimulus / fast burst)
      n_slow_pre samples at a fixed or linearly-growing spacing.
      slow_pre_mode = "constant"  ->  every sample spaced slow_pre_interval [s]
      slow_pre_mode = "linear"    ->  spacing grows from slow_pre_interval_start
                                       to slow_pre_interval_end [s]
      Set n_slow_pre = 0 to skip.

  Phase 2 – "fast"  (dense transient capture)
      n_fast samples at a fixed fast_interval [s].
      Set n_fast = 0 to skip.

  Phase 3 – "slow_post"  (long-term monitoring after the burst)
      n_slow_post samples at a fixed or linearly-growing spacing.
      slow_post_mode = "constant"  ->  every sample spaced slow_post_interval [s]
      slow_post_mode = "linear"    ->  spacing grows from slow_post_interval_start
                                        to slow_post_interval_end [s]
      Set n_slow_post = 0 to skip.

Slow-phase analysis
-------------------
After each voltage step the method  analyse_slow_post(data)  is called
automatically and prints/returns the maximum and minimum current
(and their timestamps) measured during the slow_post phase only.
You can also call it manually on any data dict returned by run().

Plot types (pass any combination in the plot list)
--------------------------------------------------
  "I_t"    – current vs elapsed time, one subplot per voltage step
               phase colours: slow_pre=green, fast=blue, slow_post=orange
  "I_log"  – same with logarithmic time axis
  "I_hist" – current histogram overlay per phase, one subplot per step
  "I_V"    – mean current (slow_post) vs set voltage, all steps overlaid

HOW TO USE
----------

  -- Three voltages, constant spacings everywhere: ------------------------

    from current_monitor_6487 import CurrentMonitor
    m = CurrentMonitor(
        k6487_resource          = "GPIB0::22::INSTR",
        voltage_list            = [100.0, 50.0, 10.0],
        n_slow_pre              = 1000,
        slow_pre_mode           = "constant",
        slow_pre_interval       = 5.0,
        n_fast                  = 1000,
        fast_interval           = 0.05,
        n_slow_post             = 1000,
        slow_post_mode          = "constant",
        slow_post_interval      = 5.0,
        nplc                    = 1,
        current_compliance      = 1e-3,
        voltage_range           = 100.0,
        settling_time           = 2.0,
        output_dir              = r"C:/Data/Measurements",
        plot                    = ["I_t", "I_log", "I_hist", "I_V"],
    )
    m.run()

  -- Linearly-growing slow_post: ------------------------------------------

    from current_monitor_6487 import CurrentMonitor
    m = CurrentMonitor(
        voltage_list                = [400.0, -400.0],
        n_slow_pre                  = 200,
        slow_pre_mode               = "constant",
        slow_pre_interval           = 5.0,
        n_fast                      = 1000,
        fast_interval               = 0.05,
        n_slow_post                 = 1000,
        slow_post_mode              = "linear",
        slow_post_interval_start    = 5.0,
        slow_post_interval_end      = 60.0,
        voltage_range               = 500.0,
        settling_time               = 120.0,
    )
    m.run()

  -- Skip slow_pre (fast + slow_post only): --------------------------------

    from current_monitor_6487 import CurrentMonitor
    m = CurrentMonitor(
        voltage_list            = [5.0],
        n_slow_pre              = 0,
        n_fast                  = 200,
        fast_interval           = 0.05,
        n_slow_post             = 500,
        slow_post_mode          = "constant",
        slow_post_interval      = 5.0,
    )
    m.run()

Dependencies:  pip install pyvisa numpy matplotlib
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
#  CurrentMonitor class
# =============================================================================

class CurrentMonitor:
    """
    Three-phase current monitor driven by a single Keithley 6487.

    Parameters
    ----------
    k6487_resource : str
        VISA resource string for the Keithley 6487.
        Default: "GPIB0::22::INSTR"
    voltage_list : list of float
        Sequence of source voltages [V] to step through.
        Each entry produces one output .txt file.
        Default: [1.0]

    -- Phase 1: slow_pre --
    n_slow_pre : int
        Samples in the pre-fast slow phase. 0 = skip.  Default: 1000
    slow_pre_mode : str
        "constant" or "linear".  Default: "constant"
    slow_pre_interval : float
        Spacing [s] when slow_pre_mode == "constant".  Default: 5.0
    slow_pre_interval_start : float
        First spacing [s] when slow_pre_mode == "linear".  Default: 5.0
    slow_pre_interval_end : float
        Last  spacing [s] when slow_pre_mode == "linear".  Default: 60.0

    -- Phase 2: fast --
    n_fast : int
        Dense samples. 0 = skip.  Default: 1000
    fast_interval : float
        Sample spacing [s] during the fast phase.  Default: 0.05

    -- Phase 3: slow_post --
    n_slow_post : int
        Samples in the post-fast slow phase. 0 = skip.  Default: 1000
    slow_post_mode : str
        "constant" or "linear".  Default: "constant"
    slow_post_interval : float
        Spacing [s] when slow_post_mode == "constant".  Default: 5.0
    slow_post_interval_start : float
        First spacing [s] when slow_post_mode == "linear".  Default: 5.0
    slow_post_interval_end : float
        Last  spacing [s] when slow_post_mode == "linear".  Default: 60.0

    -- Instrument --
    nplc : float
        Integration time in power-line cycles.  Default: 1
    current_compliance : float
        Current compliance [A].  Default: 1e-3
    voltage_range : float
        Source voltage range [V] (10, 50, or 500).  Default: 10.0
    settling_time : float
        Wait [s] after enabling source before first sample.  Default: 0.5

    -- Output --
    output_dir : str
        Directory for .txt result files.  Default: "."
    plot : list of str or None
        Any of: "I_t", "I_log", "I_hist", "I_V".  Default: ["I_t"]
    """

    _DEFAULTS = dict(
        k6487_resource              = "GPIB0::22::INSTR",
        voltage_list                = [1.0],
        # slow_pre
        n_slow_pre                  = 1000,
        slow_pre_mode               = "constant",
        slow_pre_interval           = 5.0,
        slow_pre_interval_start     = 5.0,
        slow_pre_interval_end       = 60.0,
        # fast
        n_fast                      = 1000,
        fast_interval               = 0.05,
        # slow_post
        n_slow_post                 = 1000,
        slow_post_mode              = "constant",
        slow_post_interval          = 5.0,
        slow_post_interval_start    = 5.0,
        slow_post_interval_end      = 60.0,
        # instrument
        nplc                        = 1,
        current_compliance          = 1e-3,
        voltage_range               = 10.0,
        settling_time               = 0.5,
        # output
        output_dir                  = ".",
        plot                        = ["I_t"],
    )

    _OVERFLOW_FLAGS = frozenset("ZOUH")

    def __init__(self, **kwargs):
        cfg = {**self._DEFAULTS, **kwargs}

        self.k6487_resource           = cfg["k6487_resource"]
        self.voltage_list             = list(cfg["voltage_list"])
        # slow_pre
        self.n_slow_pre               = int(cfg["n_slow_pre"])
        self.slow_pre_mode            = str(cfg["slow_pre_mode"]).lower()
        self.slow_pre_interval        = float(cfg["slow_pre_interval"])
        self.slow_pre_interval_start  = float(cfg["slow_pre_interval_start"])
        self.slow_pre_interval_end    = float(cfg["slow_pre_interval_end"])
        # fast
        self.n_fast                   = int(cfg["n_fast"])
        self.fast_interval            = float(cfg["fast_interval"])
        # slow_post
        self.n_slow_post              = int(cfg["n_slow_post"])
        self.slow_post_mode           = str(cfg["slow_post_mode"]).lower()
        self.slow_post_interval       = float(cfg["slow_post_interval"])
        self.slow_post_interval_start = float(cfg["slow_post_interval_start"])
        self.slow_post_interval_end   = float(cfg["slow_post_interval_end"])
        # instrument
        self.nplc                     = float(cfg["nplc"])
        self.current_compliance       = float(cfg["current_compliance"])
        self.voltage_range            = float(cfg["voltage_range"])
        self.settling_time            = float(cfg["settling_time"])
        # output
        self.output_dir               = cfg["output_dir"]
        self.plot                     = list(cfg["plot"]) if cfg["plot"] else []

        for mode, label in [(self.slow_pre_mode,  "slow_pre_mode"),
                            (self.slow_post_mode, "slow_post_mode")]:
            if mode not in ("constant", "linear"):
                raise ValueError(
                    f"{label} must be 'constant' or 'linear', got '{mode}'"
                )
        if not self.voltage_list:
            raise ValueError("voltage_list must contain at least one value.")
        if self.n_slow_pre + self.n_fast + self.n_slow_post == 0:
            raise ValueError(
                "At least one of n_slow_pre, n_fast, n_slow_post must be > 0."
            )

        self._rm    = None
        self._k6487 = None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self):
        """Execute the full sweep across all voltages and save results."""
        self._print_banner()
        os.makedirs(self.output_dir, exist_ok=True)

        self._rm = pyvisa.ResourceManager()
        try:
            self._connect()
            self._identify()
            self._configure_k6487()

            saved_files, all_data = self._sweep()
            self._safe_off()

            self._print_final_summary(saved_files)
            self._plot_results(all_data)

        except pyvisa.errors.VisaIOError as exc:
            print(f"\n[ERROR] VISA communication error:\n  {exc}")
            raise
        finally:
            self._safe_off()
            if self._rm:
                self._rm.close()
            print("Connections closed.")

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def _connect(self):
        print("\n[1] Opening instrument connection ...")
        print(f"    Keithley 6487  -> {self.k6487_resource}")
        self._k6487 = self._rm.open_resource(self.k6487_resource)
        self._k6487.timeout           = 10_000   # ms
        self._k6487.write_termination = "\n"
        self._k6487.read_termination  = "\n"

    def _identify(self):
        print("\n[2] Identifying instrument ...")
        self._k6487.write("*CLS")
        idn = self._k6487.query("*IDN?").strip()
        print(f"    [K6487] {idn}")

    # ------------------------------------------------------------------
    # Instrument configuration
    # ------------------------------------------------------------------

    def _configure_k6487(self):
        """
        Configure the 6487 voltage source and current measurement.
        Matches the same sequence as the Van der Pauw script.
        """
        print("\n[3] Configuring Keithley 6487 ...")
        k = self._k6487

        k.write("*RST")
        time.sleep(1.0)             # wait for reset to complete

        k.write("SYST:ZCH OFF")     # disconnect zero-check relay
        time.sleep(0.5)             # allow input relay to physically close

        # Voltage source
        k.write(f"SOUR:VOLT:RANG {self.voltage_range}")
        k.write("SOUR:VOLT 0")
        k.write(f"SOUR:VOLT:ILIM {self.current_compliance:.3E}")
        k.write("SOUR:VOLT:STAT OFF")

        # Current measurement
        k.write("SENS:FUNC 'CURR'")
        k.write("SENS:CURR:RANG:AUTO ON")
        k.write(f"SENS:CURR:NPLC {self.nplc}")

        k.write("INIT:CONT OFF")    # stop continuous buffering
        k.write("TRIG:SOUR IMM")    # trigger immediately on each READ?
        k.write("TRIG:COUN 1")      # one reading per READ?
        k.write("TRAC:CLE")         # clear any pre-run buffered samples

        print("    6487 configured.")

    # ------------------------------------------------------------------
    # Interval builders (one per slow phase)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_slow_intervals(n: int, mode: str,
                               constant: float,
                               lin_start: float,
                               lin_end: float) -> list:
        """
        Return a list of n-1 inter-sample gaps [s] for a slow phase.
        If n <= 1, returns an empty list (no gaps needed).
        """
        if n <= 1:
            return []
        n_gaps = n - 1
        if mode == "constant":
            return [constant] * n_gaps
        else:  # "linear"
            if n_gaps == 1:
                return [lin_start]
            return np.linspace(lin_start, lin_end, n_gaps).tolist()

    def _build_intervals(self) -> np.ndarray:
        """
        Build the full interval array for one voltage step.

        Layout (gaps between consecutive samples):
            slow_pre internal gaps   (n_slow_pre  - 1 entries)
            transition gap           (fast_interval, if both slow_pre and fast exist)
            fast internal gaps       (n_fast - 1 entries, all = fast_interval)
            transition gap           (fast_interval → slow_post, if both exist)
            slow_post internal gaps  (n_slow_post - 1 entries)

        Total length = n_slow_pre + n_fast + n_slow_post - 1
        """
        intervals = []

        # ── Phase 1: slow_pre ─────────────────────────────────────────
        intervals += self._build_slow_intervals(
            self.n_slow_pre,
            self.slow_pre_mode,
            self.slow_pre_interval,
            self.slow_pre_interval_start,
            self.slow_pre_interval_end,
        )

        # ── Transition slow_pre → fast ────────────────────────────────
        if self.n_slow_pre > 0 and self.n_fast > 0:
            intervals.append(self.fast_interval)

        # ── Phase 2: fast internal gaps ───────────────────────────────
        if self.n_fast > 1:
            intervals += [self.fast_interval] * (self.n_fast - 1)

        # ── Transition fast → slow_post ───────────────────────────────
        if self.n_fast > 0 and self.n_slow_post > 0:
            intervals.append(self.slow_post_interval
                             if self.slow_post_mode == "constant"
                             else self.slow_post_interval_start)

        # ── Phase 3: slow_post internal gaps ──────────────────────────
        intervals += self._build_slow_intervals(
            self.n_slow_post,
            self.slow_post_mode,
            self.slow_post_interval,
            self.slow_post_interval_start,
            self.slow_post_interval_end,
        )

        return np.array(intervals, dtype=float)

    # ------------------------------------------------------------------
    # Sweep over voltage list
    # ------------------------------------------------------------------

    def _sweep(self):
        n_steps     = len(self.voltage_list)
        saved_files = []
        all_data    = []

        print(f"\n[4] Starting sweep: {n_steps} voltage step(s) ...")

        for idx, voltage in enumerate(self.voltage_list, start=1):
            print(f"\n{'='*66}")
            print(f"  Step {idx}/{n_steps}  --  V_set = {voltage:+.4f} V")
            print(f"{'='*66}")

            data  = self._measure_step(voltage)
            fname = self._save(data, voltage, idx)
            saved_files.append(fname)
            all_data.append(data)

            # Per-step console summary
            print(f"\n  Step {idx} – overall summary:")
            print(f"    I_mean = {data['I_mean']:.4E} A  "
                  f"(+/- {data['I_std']:.2E} A)")
            print(f"    Duration: {data['total_time_s']:.1f} s  "
                  f"({data['total_time_s']/60:.1f} min)")
            if data["nan_I"]:
                print(f"    [WARNING] {data['nan_I']} overrange sample(s).")

            # Automatic slow_post analysis
            self.analyse_slow_post(data)

        return saved_files, all_data

    # ------------------------------------------------------------------
    # Single voltage step
    # ------------------------------------------------------------------

    def _measure_step(self, voltage: float) -> dict:
        """Apply voltage and collect all three phases."""
        k       = self._k6487
        n_total = self.n_slow_pre + self.n_fast + self.n_slow_post

        print(f"\n  Applying {voltage:+.4f} V  "
              f"(compliance {self.current_compliance:.2E} A)")
        k.write(f"SOUR:VOLT {voltage:.6E}")
        k.write("SOUR:VOLT:STAT ON")

        print(f"  Settling: {self.settling_time:.1f} s ...")
        time.sleep(self.settling_time)

        k.write("TRAC:CLE")     # discard readings taken during settling
        time.sleep(0.2)

        intervals  = self._build_intervals()
        currents   = np.empty(n_total)
        timestamps = np.empty(n_total)

        # Phase boundary indices
        sp_end   = self.n_slow_pre                          # slow_pre  [0 .. sp_end)
        fast_end = self.n_slow_pre + self.n_fast            # fast      [sp_end .. fast_end)
        # slow_post                                         # [fast_end .. n_total)

        t_run_start = time.perf_counter()

        for i in range(n_total):
            t_sample_start = time.perf_counter()

            currents[i]   = self._read_current()
            timestamps[i] = time.perf_counter() - t_run_start

            if i < sp_end:
                phase_label = "SLOW_PRE "
            elif i < fast_end:
                phase_label = "FAST     "
            else:
                phase_label = "SLOW_POST"

            if (i + 1) % 50 == 0 or i == 0 or i == n_total - 1:
                I_disp = (f"{currents[i]:.4E}"
                          if not np.isnan(currents[i]) else "OVERRANGE")
                print(f"    [{phase_label}] {i+1:5d}/{n_total}  "
                      f"t = {timestamps[i]:9.2f} s   I = {I_disp} A")

            if i < len(intervals):
                elapsed = time.perf_counter() - t_sample_start
                wait    = intervals[i] - elapsed
                if wait > 0:
                    time.sleep(wait)

        k.write("SOUR:VOLT:STAT OFF")
        time.sleep(0.2)

        # Phase label array
        phase = np.array(
            ["slow_pre"]  * self.n_slow_pre  +
            ["fast"]      * self.n_fast      +
            ["slow_post"] * self.n_slow_post,
            dtype=object
        )

        nan_I = int(np.sum(np.isnan(currents)))

        # Slice each phase for statistics
        I_pre  = currents[:sp_end]
        I_fast = currents[sp_end:fast_end]
        I_post = currents[fast_end:]

        def safe_stat(arr, fn):
            return float(fn(arr)) if arr.size > 0 and not np.all(np.isnan(arr)) else float("nan")

        # ── slow_pre minimum ─────────────────────────────────────────────
        pre_slice = currents[:sp_end]
        if pre_slice.size > 0 and not np.all(np.isnan(pre_slice)):
            pre_imin = int(np.nanargmin(pre_slice))          # relative index
        else:
            pre_imin = None

        # ── global maximum (all phases combined) ─────────────────────────
        if currents.size > 0 and not np.all(np.isnan(currents)):
            global_imax = int(np.nanargmax(currents))
        else:
            global_imax = None

        # ── slow_post minimum ─────────────────────────────────────────────
        post_slice = currents[fast_end:]
        if post_slice.size > 0 and not np.all(np.isnan(post_slice)):
            rel_max = int(np.nanargmax(post_slice))
            rel_min = int(np.nanargmin(post_slice))
            post_imax = fast_end + rel_max
            post_imin = fast_end + rel_min
        else:
            post_imax = post_imin = None

        return {
            "set_voltage"       : voltage,
            "timestamps"        : timestamps,
            "currents"          : currents,
            "phase"             : phase,
            "nan_I"             : nan_I,
            # overall
            "I_mean"            : safe_stat(currents,  np.nanmean),
            "I_std"             : safe_stat(currents,  np.nanstd),
            # slow_pre
            "I_pre_mean"        : safe_stat(I_pre,  np.nanmean),
            "I_pre_std"         : safe_stat(I_pre,  np.nanstd),
            "I_pre_min"         : safe_stat(I_pre,  np.nanmin),
            "I_pre_max"         : safe_stat(I_pre,  np.nanmax),
            # fast
            "I_fast_mean"       : safe_stat(I_fast, np.nanmean),
            "I_fast_std"        : safe_stat(I_fast, np.nanstd),
            "I_fast_min"        : safe_stat(I_fast, np.nanmin),
            "I_fast_max"        : safe_stat(I_fast, np.nanmax),
            # slow_post
            "I_post_mean"       : safe_stat(I_post, np.nanmean),
            "I_post_std"        : safe_stat(I_post, np.nanstd),
            "I_post_min"        : safe_stat(I_post, np.nanmin),
            "I_post_max"        : safe_stat(I_post, np.nanmax),
            "I_post_min_time"   : float(timestamps[post_imin]) if post_imin is not None else float("nan"),
            "I_post_max_time"   : float(timestamps[post_imax]) if post_imax is not None else float("nan"),
            "I_post_min_idx"    : post_imin,
            "I_post_max_idx"    : post_imax,
            "total_time_s"      : float(timestamps[-1]),
            # ── three key landmarks ──────────────────────────────────────
            # 1) minimum of slow_pre
            "landmark_pre_min"       : float(currents[pre_imin])    if pre_imin    is not None else float("nan"),
            "landmark_pre_min_time"  : float(timestamps[pre_imin])  if pre_imin    is not None else float("nan"),
            "landmark_pre_min_idx"   : pre_imin,
            # 2) maximum over ALL data
            "landmark_global_max"      : float(currents[global_imax])   if global_imax is not None else float("nan"),
            "landmark_global_max_time" : float(timestamps[global_imax]) if global_imax is not None else float("nan"),
            "landmark_global_max_idx"  : global_imax,
            "landmark_global_max_phase": str(phase[global_imax])        if global_imax is not None else "N/A",
            # 3) minimum of slow_post
            "landmark_post_min"      : float(currents[post_imin])   if post_imin   is not None else float("nan"),
            "landmark_post_min_time" : float(timestamps[post_imin]) if post_imin   is not None else float("nan"),
            "landmark_post_min_idx"  : post_imin,
        }

    # ------------------------------------------------------------------
    # Slow-post analysis  (public – can also be called manually)
    # ------------------------------------------------------------------

    def analyse_slow_post(self, data: dict) -> dict:
        """
        Print and return the min/max current statistics of the slow_post
        phase for one voltage step.

        Parameters
        ----------
        data : dict
            Data dict returned by _measure_step() / stored in all_data list.

        Returns
        -------
        dict with keys:
            I_post_min, I_post_min_time, I_post_min_idx,
            I_post_max, I_post_max_time, I_post_max_idx,
            I_post_mean, I_post_std, n_slow_post
        """
        v      = data["set_voltage"]
        n_post = int(np.sum(data["phase"] == "slow_post"))

        print(f"\n  --- slow_post analysis  (V_set = {v:+.4f} V) ---")

        if n_post == 0:
            print("    slow_post phase was not recorded (n_slow_post = 0).")
            return {}

        result = dict(
            I_post_min       = data["I_post_min"],
            I_post_min_time  = data["I_post_min_time"],
            I_post_min_idx   = data["I_post_min_idx"],
            I_post_max       = data["I_post_max"],
            I_post_max_time  = data["I_post_max_time"],
            I_post_max_idx   = data["I_post_max_idx"],
            I_post_mean      = data["I_post_mean"],
            I_post_std       = data["I_post_std"],
            n_slow_post      = n_post,
        )

        def fmtI(x):
            return f"{x:.6E}" if not np.isnan(x) else "NaN"
        def fmtT(x):
            return f"{x:.2f} s" if not np.isnan(x) else "NaN"

        def fmtIdx(x):
            return str(x) if x is not None else "N/A"

        print(f"    Samples analysed (slow_post) : {n_post}")
        print(f"    I_post_mean                  : {fmtI(result['I_post_mean'])} A  "
              f"(+/- {fmtI(result['I_post_std'])} A)")
        print(f"    I_post_MAX                   : {fmtI(result['I_post_max'])} A  "
              f"at t = {fmtT(result['I_post_max_time'])}  "
              f"(sample #{fmtIdx(result['I_post_max_idx'])})")
        print(f"    I_post_MIN                   : {fmtI(result['I_post_min'])} A  "
              f"at t = {fmtT(result['I_post_min_time'])}  "
              f"(sample #{fmtIdx(result['I_post_min_idx'])})")
        print(f"  --- Three-landmark summary ---")
        print(f"    [1] slow_pre  MIN  : {fmtI(data['landmark_pre_min'])} A  "
              f"at t = {fmtT(data['landmark_pre_min_time'])}  "
              f"(sample #{fmtIdx(data['landmark_pre_min_idx'])})")
        print(f"    [2] global    MAX  : {fmtI(data['landmark_global_max'])} A  "
              f"at t = {fmtT(data['landmark_global_max_time'])}  "
              f"(sample #{fmtIdx(data['landmark_global_max_idx'])}, "
              f"phase: {data['landmark_global_max_phase']})")
        print(f"    [3] slow_post MIN  : {fmtI(data['landmark_post_min'])} A  "
              f"at t = {fmtT(data['landmark_post_min_time'])}  "
              f"(sample #{fmtIdx(data['landmark_post_min_idx'])})")

        return result

    # ------------------------------------------------------------------
    # Single-reading helper
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_number(field: str, overflow_flags: frozenset) -> float:
        """
        Parse a float from a Keithley SCPI reading field, e.g.:
            '+1.23456E-06A'   (normal)
            '+9.91000E+37A'   (overrange -> NaN)
        """
        field = field.strip()
        m = re.match(r'([+-]?\d+\.?\d*(?:[Ee][+-]?\d+)?)', field)
        if not m:
            raise ValueError(f"No numeric value in SCPI field: {field!r}")
        numeric_str = m.group(1)
        remainder   = field[m.end():].upper()
        for unit in ("AMP", "A", "VDC", "VAC", "OHM", "V"):
            remainder = remainder.replace(unit, "")
        if any(ch in overflow_flags for ch in remainder):
            return float("nan")
        return float(numeric_str)

    def _read_current(self) -> float:
        """
        Read one current sample from the 6487 with READ?.
        Response format:  +1.23456E-06A,+1.00000E+00V,+0
        """
        raw   = self._k6487.query("READ?").strip()
        field = raw.split(",")[0]
        return self._extract_number(field, self._OVERFLOW_FLAGS)

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------

    def _save(self, data: dict, voltage: float, idx: int) -> str:
        ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(
            self.output_dir,
            f"current_monitor_{ts}_step{idx:03d}_{voltage:+.4f}V.txt"
        )

        def mode_desc(mode, const, ls, le):
            if mode == "constant":
                return f"constant {const} s"
            return f"linear {ls} s -> {le} s"

        pre_desc  = mode_desc(self.slow_pre_mode,
                              self.slow_pre_interval,
                              self.slow_pre_interval_start,
                              self.slow_pre_interval_end)
        post_desc = mode_desc(self.slow_post_mode,
                              self.slow_post_interval,
                              self.slow_post_interval_start,
                              self.slow_post_interval_end)

        def fmtI(x):
            return f"{x:.6E}" if not np.isnan(x) else "NaN"

        header = "\n".join([
            "# Current Monitor - Keithley 6487  (three-phase)",
            f"# Date/Time                  : {datetime.datetime.now().isoformat()}",
            f"# K6487 resource             : {self.k6487_resource}",
            f"# Voltage step index         : {idx} / {len(self.voltage_list)}",
            f"# Set Voltage (V)            : {voltage:.6E}",
            f"# Voltage list               : {self.voltage_list}",
            f"# -- Phase 1: slow_pre --",
            f"# n_slow_pre                 : {self.n_slow_pre}",
            f"# slow_pre spacing           : {pre_desc}",
            f"# -- Phase 2: fast --",
            f"# n_fast                     : {self.n_fast}",
            f"# fast_interval (s)          : {self.fast_interval}",
            f"# -- Phase 3: slow_post --",
            f"# n_slow_post                : {self.n_slow_post}",
            f"# slow_post spacing          : {post_desc}",
            f"# -- Instrument --",
            f"# NPLC                       : {self.nplc}",
            f"# I_compliance (A)           : {self.current_compliance:.3E}",
            f"# Voltage range (V)          : {self.voltage_range}",
            f"# Settling time (s)          : {self.settling_time}",
            f"# Total duration (s)         : {data['total_time_s']:.2f}",
            f"# -- Overall statistics --",
            f"# I_mean (A)                 : {fmtI(data['I_mean'])}",
            f"# I_std  (A)                 : {fmtI(data['I_std'])}",
            f"# -- slow_pre statistics --",
            f"# I_pre_mean (A)             : {fmtI(data['I_pre_mean'])}",
            f"# I_pre_std  (A)             : {fmtI(data['I_pre_std'])}",
            f"# I_pre_min  (A)             : {fmtI(data['I_pre_min'])}",
            f"# I_pre_max  (A)             : {fmtI(data['I_pre_max'])}",
            f"# -- fast statistics --",
            f"# I_fast_mean (A)            : {fmtI(data['I_fast_mean'])}",
            f"# I_fast_std  (A)            : {fmtI(data['I_fast_std'])}",
            f"# I_fast_min  (A)            : {fmtI(data['I_fast_min'])}",
            f"# I_fast_max  (A)            : {fmtI(data['I_fast_max'])}",
            f"# -- slow_post statistics --",
            f"# I_post_mean (A)            : {fmtI(data['I_post_mean'])}",
            f"# I_post_std  (A)            : {fmtI(data['I_post_std'])}",
            f"# I_post_min  (A)            : {fmtI(data['I_post_min'])}",
            f"# I_post_min_time (s)        : {data['I_post_min_time']:.3f}",
            f"# I_post_max  (A)            : {fmtI(data['I_post_max'])}",
            f"# I_post_max_time (s)        : {data['I_post_max_time']:.3f}",
            f"# -- Key landmarks --",
            f"# [1] slow_pre  MIN (A)      : {fmtI(data['landmark_pre_min'])}",
            f"# [1] slow_pre  MIN time (s) : {data['landmark_pre_min_time']:.3f}",
            f"# [1] slow_pre  MIN index    : {data['landmark_pre_min_idx']}",
            f"# [2] global    MAX (A)      : {fmtI(data['landmark_global_max'])}",
            f"# [2] global    MAX time (s) : {data['landmark_global_max_time']:.3f}",
            f"# [2] global    MAX index    : {data['landmark_global_max_idx']}",
            f"# [2] global    MAX phase    : {data['landmark_global_max_phase']}",
            f"# [3] slow_post MIN (A)      : {fmtI(data['landmark_post_min'])}",
            f"# [3] slow_post MIN time (s) : {data['landmark_post_min_time']:.3f}",
            f"# [3] slow_post MIN index    : {data['landmark_post_min_idx']}",
            f"# Overrange samples          : {data['nan_I']}",
            "#",
            "# index\tTime_s\tCurrent_A\tPhase",
        ])

        def fmt(x):
            return f"{x:.8E}" if not np.isnan(x) else "NaN"

        with open(fname, "w") as f:
            f.write(header + "\n")
            for i, (t, I, ph) in enumerate(
                zip(data["timestamps"], data["currents"], data["phase"])
            ):
                f.write(f"{i}\t{t:.6f}\t{fmt(I)}\t{ph}\n")

        print(f"    Saved -> {fname}")
        return fname

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def _plot_results(self, all_data: list):
        """
        Plot results after the full sweep.

        "I_t"    – current vs elapsed time (linear), one subplot per step
                   colours: slow_pre = green, fast = blue, slow_post = orange
                   min/max of slow_post marked with red/magenta markers
        "I_log"  – same with logarithmic time axis
        "I_hist" – current histogram per phase, one subplot per step
        "I_V"    – slow_post mean current vs set voltage, error bars = std
        """
        valid     = {"I_t", "I_log", "I_hist", "I_V"}
        requested = [p.strip() for p in self.plot]
        unknown   = [p for p in requested if p not in valid]
        if unknown:
            print(f"  [WARNING] Unknown plot type(s) ignored: {unknown}")
        requested = [p for p in requested if p in valid]
        if not requested:
            return

        n_steps = len(all_data)

        # Colour map per phase
        PHASE_COLOR = {
            "slow_pre"  : "tab:green",
            "fast"      : "tab:blue",
            "slow_post" : "tab:orange",
        }

        for plot_type in requested:

            # ── per-step grid: I_t / I_log / I_hist ──────────────────
            if plot_type in ("I_t", "I_log", "I_hist"):
                ncols = min(3, n_steps)
                nrows = (n_steps + ncols - 1) // ncols
                fig, axes = plt.subplots(
                    nrows, ncols,
                    figsize=(6 * ncols, 4 * nrows),
                    squeeze=False
                )

                titles = {
                    "I_t"   : "Current vs Time",
                    "I_log" : "Current vs Time (log scale)",
                    "I_hist": "Current Histogram by Phase",
                }
                fig.suptitle(titles[plot_type], fontsize=14, fontweight="bold")

                for step_idx, data in enumerate(all_data):
                    ax    = axes[step_idx // ncols][step_idx % ncols]
                    t     = data["timestamps"]
                    I     = data["currents"]
                    ph    = data["phase"]
                    v_set = data["set_voltage"]

                    if plot_type in ("I_t", "I_log"):
                        t_plot = t.copy()
                        if plot_type == "I_log" and t_plot[0] == 0:
                            pos_t     = t_plot[t_plot > 0]
                            t_plot[0] = pos_t[0] / 2 if len(pos_t) else 1e-3

                        plot_fn = ax.semilogx if plot_type == "I_log" else ax.plot

                        for phase_name in ("slow_pre", "fast", "slow_post"):
                            mask = (ph == phase_name)
                            if mask.any():
                                n_ph = int(mask.sum())
                                plot_fn(t_plot[mask], I[mask],
                                        color=PHASE_COLOR[phase_name],
                                        linewidth=0.9,
                                        label=f"{phase_name} ({n_ph} pts)")

                        # Mark the three key landmarks
                        if data["landmark_pre_min_idx"] is not None:
                            i1 = data["landmark_pre_min_idx"]
                            ax.plot(t_plot[i1], I[i1],
                                    "v", color="darkgreen", markersize=8,
                                    zorder=5,
                                    label=f"[1] pre_MIN  {data['landmark_pre_min']:.3E} A")
                        if data["landmark_global_max_idx"] is not None:
                            i2 = data["landmark_global_max_idx"]
                            ax.plot(t_plot[i2], I[i2],
                                    "*", color="red", markersize=10,
                                    zorder=5,
                                    label=f"[2] glob_MAX {data['landmark_global_max']:.3E} A")
                        if data["landmark_post_min_idx"] is not None:
                            i3 = data["landmark_post_min_idx"]
                            ax.plot(t_plot[i3], I[i3],
                                    "v", color="darkorange", markersize=8,
                                    zorder=5,
                                    label=f"[3] post_MIN {data['landmark_post_min']:.3E} A")

                        ax.set_xlabel(
                            "Time (s) [log]" if plot_type == "I_log"
                            else "Elapsed time (s)"
                        )
                        ax.set_ylabel("Current (A)")
                        ax.legend(fontsize=7, loc="best")
                        ax.grid(True,
                                which="both" if plot_type == "I_log" else "major",
                                linestyle="--", alpha=0.5)

                    else:  # "I_hist"
                        for phase_name in ("slow_pre", "fast", "slow_post"):
                            mask    = (ph == phase_name)
                            I_clean = I[mask & ~np.isnan(I)]
                            if I_clean.size == 0:
                                continue
                            bins = max(15, int(np.sqrt(I_clean.size)))
                            ax.hist(I_clean, bins=bins,
                                    color=PHASE_COLOR[phase_name],
                                    alpha=0.6, edgecolor="white",
                                    linewidth=0.4,
                                    label=f"{phase_name} ({I_clean.size} pts)")
                        ax.set_xlabel("Current (A)")
                        ax.set_ylabel("Count")
                        ax.legend(fontsize=7)
                        ax.grid(True, linestyle="--", alpha=0.5)

                    ax.set_title(f"V_set = {v_set:+.2f} V")

                for step_idx in range(n_steps, nrows * ncols):
                    axes[step_idx // ncols][step_idx % ncols].set_visible(False)

                fig.tight_layout()
                plt.show()

            # ── I(V): slow_post mean vs set voltage ───────────────────
            elif plot_type == "I_V":
                fig, ax = plt.subplots(figsize=(7, 5))
                fig.suptitle("slow_post Mean Current vs Set Voltage",
                             fontsize=14, fontweight="bold")

                voltages = [d["set_voltage"]  for d in all_data]
                means    = [d["I_post_mean"]  for d in all_data]
                stds     = [d["I_post_std"]   for d in all_data]

                ax.errorbar(voltages, means, yerr=stds,
                            fmt="o-", color="tab:orange", capsize=4,
                            linewidth=1.2, markersize=6,
                            label="slow_post  I_mean +/- I_std")
                ax.set_xlabel("Set Voltage (V)")
                ax.set_ylabel("Mean Current – slow_post (A)")
                ax.legend(fontsize=9)
                ax.grid(True, linestyle="--", alpha=0.5)
                fig.tight_layout()
                plt.show()

    # ------------------------------------------------------------------
    # Safety
    # ------------------------------------------------------------------

    def _safe_off(self):
        """Zero and disable the 6487 source."""
        try:
            if self._k6487:
                self._k6487.write("SOUR:VOLT 0")
                self._k6487.write("SOUR:VOLT:STAT OFF")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Banner / summary
    # ------------------------------------------------------------------

    def _est_phase_time(self, n, mode, const, ls, le):
        if n == 0:
            return 0.0
        if mode == "constant":
            return n * const
        return n * (ls + le) / 2

    def _print_banner(self):
        n_total = self.n_slow_pre + self.n_fast + self.n_slow_post

        def mode_desc(mode, const, ls, le):
            if mode == "constant":
                return f"constant {const} s"
            return f"linear {ls} s -> {le} s"

        t_pre  = self._est_phase_time(self.n_slow_pre,  self.slow_pre_mode,
                                       self.slow_pre_interval,
                                       self.slow_pre_interval_start,
                                       self.slow_pre_interval_end)
        t_fast = self.n_fast * self.fast_interval
        t_post = self._est_phase_time(self.n_slow_post, self.slow_post_mode,
                                       self.slow_post_interval,
                                       self.slow_post_interval_start,
                                       self.slow_post_interval_end)
        t_step  = self.settling_time + t_pre + t_fast + t_post
        t_total = t_step * len(self.voltage_list)

        print("=" * 66)
        print("  Current Monitor  -  Keithley 6487  (three-phase)")
        print("=" * 66)
        print(f"  6487 resource           : {self.k6487_resource}")
        print(f"  Voltage list            : {self.voltage_list} V")
        print(f"  Number of steps         : {len(self.voltage_list)}")
        print(f"  Current compliance      : {self.current_compliance:.2E} A")
        print(f"  Voltage range           : {self.voltage_range} V")
        print(f"  NPLC                    : {self.nplc}")
        print(f"  Settling time           : {self.settling_time} s / step")
        print(f"  --- Sampling schedule (per step) ---")
        print(f"  Phase 1  slow_pre       : {self.n_slow_pre} pts  "
              f"spacing: {mode_desc(self.slow_pre_mode, self.slow_pre_interval, self.slow_pre_interval_start, self.slow_pre_interval_end)}"
              f"  (~{t_pre:.0f} s)")
        print(f"  Phase 2  fast           : {self.n_fast} pts  "
              f"interval: {self.fast_interval} s  "
              f"(~{t_fast:.0f} s)")
        print(f"  Phase 3  slow_post      : {self.n_slow_post} pts  "
              f"spacing: {mode_desc(self.slow_post_mode, self.slow_post_interval, self.slow_post_interval_start, self.slow_post_interval_end)}"
              f"  (~{t_post:.0f} s)")
        print(f"  Total / step            : {n_total} samples,  "
              f"~{t_step:.0f} s  ({t_step/60:.1f} min)")
        print(f"  Est. total duration     : ~{t_total:.0f} s  "
              f"({t_total/60:.1f} min  /  {t_total/3600:.2f} h)")
        print(f"  Output dir              : {os.path.abspath(self.output_dir)}")
        print(f"  Plot types              : {self.plot}")
        print("=" * 66)

    def _print_final_summary(self, saved_files: list):
        print("\n" + "=" * 66)
        print("  All steps complete.")
        print(f"  {len(saved_files)} file(s) saved to: "
              f"{os.path.abspath(self.output_dir)}")
        for f in saved_files:
            print(f"    {os.path.basename(f)}")
        print("=" * 66)



# =============================================================================
#  Convenience entry point – run directly:  python current_monitor_6487.py
#  Or paste/edit the block below into a Spyder cell and press Ctrl+Enter.
# =============================================================================

if __name__ == "__main__":
    #'''
    # ── Example 1: three voltages, fast burst then constant slow interval ──
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
    '''
    #dark before illumination
    m = CurrentMonitor(
        k6487_resource              = "GPIB0::22::INSTR",  # << adjust

        # Voltage steps – one file per voltage
        voltage_list                = [10, 50, 100],  # V

        # Phase 1 – slow baseline before the burst
        n_slow_pre                  = 200,
        slow_pre_mode               = "constant",
        slow_pre_interval           = 1.0,                  # 5 s between pts

        # Phase 2 – dense transient capture
        n_fast                      = 0,
        fast_interval               = 0.05,                 # 50 ms -> 20 Hz

        # Phase 3 – long-term monitoring after burst
        n_slow_post                 = 0,
        slow_post_mode              = "constant",
        slow_post_interval          = 1.0,                  # 5 s between pts

        # Instrument
        nplc                        = 1,
        current_compliance          = 2.5e-3,
        voltage_range               = 500.0,
        settling_time               = 60.0,

        # ── Output ──────────────────────────────────────────────────────────
        output_dir          = r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\PN_Junc\TiO2\DC-MAG\TiO2_068_SAP_A\Dark_bef",
        plot                = ["I_t", "I_log"],
        )
    '''
    m.run()

    # ── Example 2 (commented): linear slow_post, high voltage ─────────────
    # m = CurrentMonitor(
    #     k6487_resource              = "GPIB0::22::INSTR",
    #     voltage_list                = [400.0, -400.0],
    #     n_slow_pre                  = 200,
    #     slow_pre_mode               = "constant",
    #     slow_pre_interval           = 5.0,
    #     n_fast                      = 1000,
    #     fast_interval               = 0.05,
    #     n_slow_post                 = 1000,
    #     slow_post_mode              = "linear",
    #     slow_post_interval_start    = 5.0,
    #     slow_post_interval_end      = 60.0,
    #     nplc                        = 1,
    #     current_compliance          = 1e-3,
    #     voltage_range               = 500.0,
    #     settling_time               = 120.0,
    #     output_dir                  = r"C:\Data\Measurements",
    #     plot                        = ["I_t", "I_log", "I_V"],
    # )
    # m.run()