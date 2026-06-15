# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
current_plotter.py
==================
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
"""

import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# =============================================================================
#  -- USER SETTINGS ------------------------------------------------------------
# =============================================================================

ROOT_DIR = r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\PN_Junc\TiO2"

# =============================================================================
#  -- FILE DISCOVERY -----------------------------------------------------------
# =============================================================================

def _is_measurement_file(fname: str) -> bool:
    return fname.startswith("current_monitor_") and fname.endswith(".txt")


def scan_files(root: str) -> list:
    """
    Walk *root* and return a list of file-info dicts, one per .txt file.

    Each dict contains:
        index   - integer catalogue index
        path    - full absolute path
        method  - subfolder directly under root  (e.g. "DC-MAG")
        sample  - subfolder under method         (e.g. "TiO2_067_SAP")
        dark    - True when the file is inside a Dark_bef subfolder
        voltage - set voltage parsed from the filename (float), or None
        label   - short human-readable label
    """
    files = []
    idx   = 0
    root  = os.path.abspath(root)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fname in sorted(filenames):
            if not _is_measurement_file(fname):
                continue

            full_path = os.path.join(dirpath, fname)
            rel       = os.path.relpath(dirpath, root)
            parts     = rel.replace("\\", "/").split("/")

            method  = parts[0] if len(parts) >= 1 else "?"
            sample  = parts[1] if len(parts) >= 2 else "?"
            dark    = "dark" in rel.lower()
            voltage = _parse_voltage(fname)
            label   = (f"{method}/{sample}"
                       f"{'[DARK]' if dark else ''}  {_fmt_v(voltage)}")

            files.append({
                "index"  : idx,
                "path"   : full_path,
                "method" : method,
                "sample" : sample,
                "dark"   : dark,
                "voltage": voltage,
                "label"  : label,
            })
            idx += 1

    return files


def _parse_voltage(fname: str):
    """
    Extract the set voltage (float) from filenames like:
        current_monitor_20260331_131541_step001_+10.0000V.txt
        current_monitor_20260331_151545_step001__10_0000V.txt
    Returns float or None.
    """
    # Standard form: _+10.0000V or _-100.0000V
    m = re.search(r'_([+-]\d+\.\d+)V\.txt$', fname, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    # Windows workaround: __10_0000V  (double-underscore = +, underscore = dot)
    m = re.search(r'__(\d+)_(\d+)V\.txt$', fname, re.IGNORECASE)
    if m:
        try:
            return float(f"{m.group(1)}.{m.group(2)}")
        except ValueError:
            pass
    # Last resort: any float before V.txt
    m = re.search(r'([\d.]+)V\.txt$', fname, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def _fmt_v(v) -> str:
    return "?V" if v is None else f"{v:+.0f} V"


# =============================================================================
#  -- CATALOGUE DISPLAY --------------------------------------------------------
# =============================================================================

def show_catalogue(files: list) -> None:
    if not files:
        print("No measurement files found.  Check ROOT_DIR.")
        return

    print("\n" + "=" * 80)
    print(f"  File catalogue  -  root: {ROOT_DIR}")
    print("=" * 80)
    print(f"  {'#':>4}  {'Method':<14}  {'Sample':<20}  "
          f"{'Dark':<5}  {'Voltage':>8}  Filename")
    print("-" * 80)
    for f in files:
        print(f"  {f['index']:>4}  {f['method']:<14}  {f['sample']:<20}  "
              f"{'yes' if f['dark'] else 'no':<5}  {_fmt_v(f['voltage']):>8}  "
              f"{os.path.basename(f['path'])}")
    print("=" * 80)
    print(f"  Total: {len(files)} file(s)")
    print("  Use mrun([...]) to select files by index.\n")


# =============================================================================
#  -- FILE READER --------------------------------------------------------------
# =============================================================================

def load_file(path: str) -> dict:
    """Parse one .txt measurement file produced by Current_measurement.py."""
    header     = {}
    timestamps = []
    currents   = []
    phases     = []

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if line.startswith("#"):
                content = line.lstrip("#").strip()
                if ":" in content:
                    key, _, val = content.partition(":")
                    header[key.strip()] = val.strip()
            else:
                parts = line.split("\t")
                if len(parts) >= 4:
                    try:
                        timestamps.append(float(parts[1]))
                        val = parts[2].strip()
                        currents.append(
                            float(val) if val.upper() != "NAN" else np.nan
                        )
                        phases.append(parts[3].strip())
                    except ValueError:
                        pass

    return {
        "path"      : path,
        "header"    : header,
        "timestamps": np.array(timestamps),
        "currents"  : np.array(currents),
        "phase"     : np.array(phases, dtype=object),
    }


# =============================================================================
#  -- INDEX PARSING HELPER -----------------------------------------------------
# =============================================================================

def _parse_indices(selection, n_files: int) -> list:
    if isinstance(selection, str) and selection.strip().lower() == "all":
        return list(range(n_files))
    if not isinstance(selection, (list, tuple)):
        selection = [selection]

    indices = []
    for item in selection:
        if isinstance(item, int):
            indices.append(item)
        elif isinstance(item, str):
            item = item.strip()
            m = re.match(r'^(\d+)\s*-\s*(\d+)$', item)
            if m:
                indices.extend(range(int(m.group(1)), int(m.group(2)) + 1))
            else:
                indices.append(int(item))
        else:
            raise ValueError(f"Cannot parse index: {item!r}")

    valid   = [i for i in indices if 0 <= i < n_files]
    invalid = [i for i in indices if not (0 <= i < n_files)]
    if invalid:
        print(f"  [WARNING] Indices out of range and skipped: {invalid}")
    return sorted(set(valid))


# =============================================================================
#  -- COLOUR / STYLE ASSIGNMENT ------------------------------------------------
# =============================================================================

_TAB10 = plt.cm.tab10.colors  # type: ignore[attr-defined]


def _file_style(file_rank: int, is_dark: bool) -> dict:
    return {
        "linestyle" : "--" if is_dark else "-",
        "color"     : _TAB10[file_rank % len(_TAB10)],
        "alpha"     : 0.70 if is_dark else 0.90,
        "linewidth" : 1.1,
    }


# =============================================================================
#  -- ANALYTICS ----------------------------------------------------------------
# =============================================================================

def _mean_dark_current(data: dict) -> float:
    """
    Return the mean |I| of the slow_pre phase, or of all valid samples
    as a fallback.  Used when no separate Dark_bef file is in the selection.
    """
    I  = data["currents"]
    ph = data["phase"]

    mask = (ph == "slow_pre") & ~np.isnan(I)
    if mask.any():
        return float(np.mean(np.abs(I[mask])))

    valid = I[~np.isnan(I)]
    if valid.size > 0:
        return float(np.mean(np.abs(valid)))
    return float("nan")


def _peak_and_decay(data: dict):
    """
    Locate the global peak (max |I|) and compute the elapsed time after that
    peak at which |I| decays to:
        I_peak / 2       (half)
        I_peak / 10      (one decade)
        I_peak / 100     (two decades)

    The search for each threshold begins strictly after the peak sample, so
    we are always looking at the falling (post-illumination) edge.

    Returns
    -------
    peak_I  : float  - signed peak current value
    peak_t  : float  - time of the peak
    t_half  : float  - time of half-peak crossing  (inf if never reached)
    t_1dec  : float  - time of 1-decade drop        (inf if never reached)
    t_2dec  : float  - time of 2-decade drop        (inf if never reached)
    """
    t = data["timestamps"]
    I = data["currents"]

    valid_mask = ~np.isnan(I)
    if not valid_mask.any():
        nan = float("nan")
        return nan, nan, float("inf"), float("inf"), float("inf")

    peak_idx = int(np.nanargmax(np.abs(I)))
    peak_I   = float(I[peak_idx])
    peak_t   = float(t[peak_idx])
    peak_abs = abs(peak_I)

    post_mask = np.arange(len(t)) > peak_idx
    results   = {}

    for key, thr in [("half", peak_abs / 2.0),
                     ("1dec", peak_abs / 10.0),
                     ("2dec", peak_abs / 100.0)]:
        if not post_mask.any():
            results[key] = float("inf")
        else:
            t_post = t[post_mask]
            I_post = np.abs(I[post_mask])
            below  = np.where((~np.isnan(I_post)) & (I_post <= thr))[0]
            results[key] = float(t_post[below[0]]) if below.size > 0 else float("inf")

    return peak_I, peak_t, results["half"], results["1dec"], results["2dec"]


def _resolve_dark_mean(data: dict, all_datasets: list) -> float:
    """
    For an illuminated dataset find the best available dark-current reference:
      1. A Dark_bef file in the current selection with matching method/sample/voltage.
      2. The slow_pre phase within this file itself.
    """
    fi = data["meta"]
    for ds in all_datasets:
        ds_fi = ds["meta"]
        if (ds_fi["dark"]
                and ds_fi["method"]  == fi["method"]
                and ds_fi["sample"]  == fi["sample"]
                and ds_fi["voltage"] == fi["voltage"]):
            I_d   = ds["currents"]
            valid = I_d[~np.isnan(I_d)]
            if valid.size > 0:
                return float(np.mean(np.abs(valid)))

    return _mean_dark_current(data)


# =============================================================================
#  -- CONSOLE SUMMARY ----------------------------------------------------------
# =============================================================================

def _print_analytics(datasets: list, decay_markers: bool) -> None:
    illuminated = [d for d in datasets if not d["meta"]["dark"]]
    if not illuminated:
        return

    w = 92
    print("\n" + "=" * w)
    print("  Analytics summary  (illuminated files only)")
    print("=" * w)
    print(f"  {'Label':<44}  {'Dark mean (A)':>14}  {'Peak (A)':>13}  "
          f"{'t_peak (s)':>10}  {'t1/2 (s)':>10}  {'t/10 (s)':>10}  {'t/100 (s)':>10}")
    print("-" * w)

    for data in illuminated:
        dark_mean                     = _resolve_dark_mean(data, datasets)
        peak_I, peak_t, t_half, t_1dec, t_2dec = _peak_and_decay(data)

        def fI(x):
            return f"{x:.3E}" if (not np.isnan(x)) else "NaN"

        def ft(x):
            return _fmt_time(x)

        lbl = data["meta"]["label"][:43]
        print(f"  {lbl:<44}  {fI(dark_mean):>14}  {fI(peak_I):>13}  "
              f"{ft(peak_t):>10}  {ft(t_half):>10}  {ft(t_1dec):>10}  {ft(t_2dec):>10}")

    print("=" * w + "\n")


def _fmt_time(t: float) -> str:
    if np.isnan(t):
        return "NaN"
    if np.isinf(t):
        return "inf"
    return f"{t:.1f} s"


# =============================================================================
#  -- CORE DRAW FUNCTION -------------------------------------------------------
# =============================================================================

def _draw_trace(ax_lin, ax_log, data: dict, style: dict,
                file_handles: list) -> None:
    """Draw the raw I(t) trace for one dataset on both axes."""
    t = data["timestamps"]
    I = data["currents"]

    # Linear
    ax_lin.plot(t, I,
                color=style["color"],
                linestyle=style["linestyle"],
                alpha=style["alpha"],
                linewidth=style["linewidth"])

    # Log |I|
    I_abs = np.abs(I)
    valid = (I_abs > 0) & ~np.isnan(I)
    if valid.any():
        ax_log.semilogy(t[valid], I_abs[valid],
                        color=style["color"],
                        linestyle=style["linestyle"],
                        alpha=style["alpha"],
                        linewidth=style["linewidth"])

    file_handles.append(mlines.Line2D(
        [], [],
        color=style["color"],
        linestyle=style["linestyle"],
        linewidth=2,
        label=data["meta"]["label"],
    ))


# =============================================================================
#  -- ANNOTATION FUNCTION ------------------------------------------------------
# =============================================================================

# Marker shapes for the three decay thresholds
_DECAY_MARKER_STYLE = {
    "half" : ("v", "t(I_peak/2)"),
    "1dec" : ("s", "t(I_peak/10)"),
    "2dec" : ("o", "t(I_peak/100)"),
}


def _annotate_file(ax_lin, ax_log, data: dict, style: dict,
                   dark_mean: float, decay_markers: bool,
                   annotation_handles: list) -> None:
    """
    Draw per-file annotations onto both axes and append legend handles:
      - dotted horizontal line for mean dark current
      - star for the peak current
      - decay threshold markers (if decay_markers=True)
    """
    t   = data["timestamps"]
    I   = data["currents"]
    col = style["color"]
    lbl = data["meta"]["label"]

    peak_I, peak_t, t_half, t_1dec, t_2dec = _peak_and_decay(data)

    # ---- Mean dark current horizontal line ----------------------------------
    if not np.isnan(dark_mean):
        for ax in (ax_lin, ax_log):
            ax.axhline(dark_mean,
                       color=col, linestyle=":", linewidth=1.3, alpha=0.80)

        annotation_handles.append(mlines.Line2D(
            [], [], color=col, linestyle=":", linewidth=1.5,
            label=f"{lbl}  |I_dark| mean = {dark_mean:.3E} A",
        ))

    # ---- Peak marker --------------------------------------------------------
    if not np.isnan(peak_t):
        ax_lin.plot(peak_t, peak_I,
                    "*", color=col, markersize=12, zorder=5,
                    markeredgecolor="black", markeredgewidth=0.4)
        if abs(peak_I) > 0:
            ax_log.plot(peak_t, abs(peak_I),
                        "*", color=col, markersize=12, zorder=5,
                        markeredgecolor="black", markeredgewidth=0.4)

        annotation_handles.append(mlines.Line2D(
            [], [], color=col, marker="*", linestyle="None",
            markersize=10, markeredgecolor="black", markeredgewidth=0.4,
            label=f"{lbl}  I_peak = {peak_I:.3E} A  @ {_fmt_time(peak_t)}",
        ))

    # ---- Decay threshold markers --------------------------------------------
    if decay_markers and not np.isnan(peak_t):
        decay_data = [
            ("half", t_half, peak_I / 2.0),
            ("1dec", t_1dec, peak_I / 10.0),
            ("2dec", t_2dec, peak_I / 100.0),
        ]

        for key, dt, threshold_I in decay_data:
            marker_shape, marker_name = _DECAY_MARKER_STYLE[key]

            # Draw marker only when the threshold was actually reached
            if np.isfinite(dt) and not np.isnan(dt) and dt <= t[-1]:
                ax_lin.plot(dt, threshold_I,
                            marker_shape, color=col,
                            markersize=8, zorder=5,
                            markeredgecolor="black", markeredgewidth=0.5)
                if abs(threshold_I) > 0:
                    ax_log.plot(dt, abs(threshold_I),
                                marker_shape, color=col,
                                markersize=8, zorder=5,
                                markeredgecolor="black", markeredgewidth=0.5)

            annotation_handles.append(mlines.Line2D(
                [], [], color=col, marker=marker_shape, linestyle="None",
                markersize=7, markeredgecolor="black", markeredgewidth=0.5,
                label=f"{lbl}  {marker_name} = {_fmt_time(dt)}",
            ))


# =============================================================================
#  -- AXIS / LEGEND HELPERS ----------------------------------------------------
# =============================================================================

def _apply_ax_labels(ax, ylabel: str) -> None:
    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(True, which="both", linestyle="--", alpha=0.45)


def _build_legends(ax, file_handles: list, annotation_handles: list) -> None:
    """
    Two legends per axes:
      upper-right  - trace lines (one per file)
      lower-right  - annotations (dark mean, peak, decay times)
    """
    if file_handles:
        leg1 = ax.legend(
            handles=file_handles,
            title="Traces", loc="upper right", fontsize=7,
            framealpha=0.85,
        )
        ax.add_artist(leg1)
    if annotation_handles:
        ax.legend(
            handles=annotation_handles,
            title="Annotations", loc="lower right", fontsize=6.5,
            framealpha=0.80,
        )


def _add_linestyle_key(ax) -> None:
    """Small inset legend explaining solid vs dashed line styles."""
    handles = [
        mlines.Line2D([], [], color="grey", linestyle="-",  linewidth=1.5,
                      label="illuminated"),
        mlines.Line2D([], [], color="grey", linestyle="--", linewidth=1.5,
                      label="dark"),
    ]
    leg = ax.legend(handles=handles, loc="upper center", fontsize=6.5,
                    framealpha=0.70, ncol=2)
    ax.add_artist(leg)


# =============================================================================
#  -- OVERLAY MODE -------------------------------------------------------------
# =============================================================================

def _plot_overlay(datasets: list, decay_markers: bool) -> None:
    """All traces on a single pair of axes (1 linear + 1 log figure)."""

    fig_lin, ax_lin = plt.subplots(figsize=(13, 5))
    fig_log, ax_log = plt.subplots(figsize=(13, 5))

    _apply_ax_labels(ax_lin, "Current (A)  [linear]")
    _apply_ax_labels(ax_log, "Current (A)  [log |I|]")

    title = ("Current vs Time  -  overlay\n" +
             ",  ".join(d["meta"]["label"] for d in datasets))
    for fig in (fig_lin, fig_log):
        fig.suptitle(title, fontsize=9, fontweight="bold", wrap=True)

    file_handles:       list = []
    annotation_handles: list = []

    for rank, data in enumerate(datasets):
        style = _file_style(rank, data["meta"]["dark"])
        _draw_trace(ax_lin, ax_log, data, style, file_handles)

        if not data["meta"]["dark"]:
            dark_mean = _resolve_dark_mean(data, datasets)
            _annotate_file(ax_lin, ax_log, data, style,
                           dark_mean, decay_markers, annotation_handles)

    for ax in (ax_lin, ax_log):
        _add_linestyle_key(ax)
        _build_legends(ax, file_handles, annotation_handles)

    fig_lin.tight_layout()
    fig_log.tight_layout()
    fig_lin.canvas.manager.set_window_title("Overlay - linear Y")
    fig_log.canvas.manager.set_window_title("Overlay - log |I| Y")
    plt.show()


# =============================================================================
#  -- SIDE-BY-SIDE MODE --------------------------------------------------------
# =============================================================================

def _plot_side(datasets: list, decay_markers: bool) -> None:
    """
    One subplot column per file.
    Row 0 = linear Y,  Row 1 = log |I| Y.
    Both rows of the same column share the same x-axis (linked).
    """
    n   = len(datasets)
    fig, axes = plt.subplots(
        nrows=2, ncols=n,
        figsize=(max(5, 5.5 * n), 9),
        sharex="col",
        squeeze=False,
    )
    fig.suptitle("Current vs Time  -  side by side",
                 fontsize=11, fontweight="bold")

    for col, data in enumerate(datasets):
        fi    = data["meta"]
        style = _file_style(col, fi["dark"])

        ax_lin = axes[0][col]
        ax_log = axes[1][col]

        file_handles:       list = []
        annotation_handles: list = []

        _draw_trace(ax_lin, ax_log, data, style, file_handles)

        if not fi["dark"]:
            dark_mean = _resolve_dark_mean(data, datasets)
            _annotate_file(ax_lin, ax_log, data, style,
                           dark_mean, decay_markers, annotation_handles)

        ax_lin.set_title(fi["label"], fontsize=7.5, wrap=True)

        if col == 0:
            _apply_ax_labels(ax_lin, "Current (A)  [linear]")
            _apply_ax_labels(ax_log, "Current (A)  [log |I|]")
        else:
            ax_lin.set_xlabel("Time (s)", fontsize=9)
            ax_log.set_xlabel("Time (s)", fontsize=9)
            ax_lin.grid(True, which="both", linestyle="--", alpha=0.45)
            ax_log.grid(True, which="both", linestyle="--", alpha=0.45)

        for ax in (ax_lin, ax_log):
            _add_linestyle_key(ax)
            _build_legends(ax, file_handles, annotation_handles)

    fig.tight_layout()
    fig.canvas.manager.set_window_title(
        "Side by side - linear (top) / log (bottom)")
    plt.show()


# =============================================================================
#  -- PUBLIC API ---------------------------------------------------------------
# =============================================================================

_FILES: list = []


def _ensure_scanned() -> None:
    global _FILES
    if not _FILES:
        _FILES = scan_files(ROOT_DIR)
        show_catalogue(_FILES)


def mrun(selection,
         mode: str           = "overlay",
         decay_markers: bool = True) -> None:
    """
    Select and plot files by catalogue index.

    Parameters
    ----------
    selection : int | str | list
        File indices to plot.  Examples:
            mrun(0)                          # single file
            mrun([0, 1, 2])                  # three files
            mrun("0-2")                      # inclusive range
            mrun([0, "3-5", 9])              # mixed list
            mrun("all")                      # all files

    mode : str, optional
        "overlay"  (default) - all traces on a single pair of axes.
        "side"               - one subplot column per file
                               (top = linear Y, bottom = log |I|).

    decay_markers : bool, optional
        True  (default) - annotate the times after the current peak where
                          the signal falls to I_peak/2,  I_peak/10, and
                          I_peak/100.  The times appear in the legend;
                          if a threshold is never reached it shows as inf.
        False           - omit decay-time markers (cleaner plot for quick
                          comparisons where decay is not the focus).

    A console summary table with dark-mean, peak, and all decay times is
    always printed regardless of the decay_markers setting.
    Two matplotlib figures are opened (linear Y + log |I| Y).
    """
    _ensure_scanned()

    mode = mode.strip().lower()
    if mode not in ("overlay", "side"):
        print(f"  [WARNING] Unknown mode '{mode}'. Using 'overlay'.")
        mode = "overlay"

    indices = _parse_indices(selection, len(_FILES))
    if not indices:
        print("  No valid indices selected.")
        return

    chosen = [_FILES[i] for i in indices]

    print(f"\n  Plotting {len(chosen)} file(s)  "
          f"[mode={mode},  decay_markers={decay_markers}]:")
    for f in chosen:
        print(f"    [{f['index']:>3}]  {f['label']}")
        print(f"           {f['path']}")
    print()

    datasets = []
    for fi in chosen:
        try:
            data = load_file(fi["path"])
            data["meta"] = fi
            datasets.append(data)
        except Exception as exc:
            print(f"  [ERROR] Could not load {fi['path']}: {exc}")

    if not datasets:
        print("  No files loaded successfully.")
        return

    _print_analytics(datasets, decay_markers)

    if mode == "side":
        _plot_side(datasets, decay_markers)
    else:
        _plot_overlay(datasets, decay_markers)


def reload() -> None:
    """Force a rescan of the directory tree and reprint the catalogue."""
    global _FILES
    _FILES = []
    _ensure_scanned()

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