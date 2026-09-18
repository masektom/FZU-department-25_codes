#!/usr/bin/env python3
# =============================================================================
#  Modified Scherrer crystal size from powder XRD
#
#  Implements Nasiri et al., Nano Trends 3 (2023) 100015:
#
#       beta = (K*lambda / L) * 1/cos(theta)
#       ln(beta) = ln(1/cos theta) + ln(K*lambda / L)
#
#  A least squares fit of ln(beta) [rad] vs ln(1/cos theta) gives
#       slope     -> should land near 1 (quality check)
#       intercept -> L = K*lambda / exp(intercept)
#
#  Paper rules: (1) slope close to 1; (2) delete outlier peaks one at a time
#  until it is, never dropping below 5 peaks; (3) with <=5 peaks from the
#  start, a slope below 10 is still acceptable.
#
#  WORKFLOW
#  --------
#  Pass 1:  set dry_run = True. Every peak in the pattern is detected, fitted
#           and listed with an ID (P1, P2, P3 ...). Nothing is calculated yet.
#  Pass 2:  put the IDs of the peaks belonging to your phase into use_peaks,
#           set dry_run = False, and rerun. The script fits those peaks, checks
#           the slope, and prunes outliers automatically until it is near 1.
#
#  use_peaks = None does the same thing without the manual step, taking the
#  most intense peaks instead - useful for a quick look or a single phase.
#
#  Run directly:  python modified_scherrer.py
#  Or paste/edit the config block at the bottom into a Spyder cell (Ctrl+Enter).
# =============================================================================

import os

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks


# =============================================================================
#  PEAK PROFILE FUNCTIONS
# =============================================================================
def gaussian(x, amp, ctr, fwhm):
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    return amp * np.exp(-0.5 * ((x - ctr) / sigma) ** 2)


def lorentzian(x, amp, ctr, fwhm):
    gamma = fwhm / 2
    return amp * gamma ** 2 / ((x - ctr) ** 2 + gamma ** 2)


def pseudo_voigt(x, amp, ctr, fwhm, eta):
    eta = np.clip(eta, 0.0, 1.0)
    return eta * lorentzian(x, amp, ctr, fwhm) + (1 - eta) * gaussian(x, amp, ctr, fwhm)


def _profile_model(name):
    if name == "gaussian":
        return (lambda x, amp, ctr, fwhm, sl, cn:
                gaussian(x, amp, ctr, fwhm) + sl * x + cn), 5
    if name == "lorentzian":
        return (lambda x, amp, ctr, fwhm, sl, cn:
                lorentzian(x, amp, ctr, fwhm) + sl * x + cn), 5
    return (lambda x, amp, ctr, fwhm, eta, sl, cn:
            pseudo_voigt(x, amp, ctr, fwhm, eta) + sl * x + cn), 6


def linear_fit(x, y):
    """Least squares y = a + b*x with standard errors and R^2."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    if n < 2:
        raise ValueError("Need at least 2 points for a linear fit")
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    if n > 2:
        s2 = np.sum(resid ** 2) / (n - 2)
        sxx = np.sum((x - x.mean()) ** 2)
        b_err = np.sqrt(s2 / sxx)
        a_err = np.sqrt(s2 * (1 / n + x.mean() ** 2 / sxx))
    else:
        b_err = a_err = np.nan
    ss_tot = np.sum((y - y.mean()) ** 2)
    return {"slope": b, "slope_err": b_err, "intercept": a, "intercept_err": a_err,
            "r2": 1 - np.sum(resid ** 2) / ss_tot if ss_tot > 0 else np.nan,
            "rss": float(np.sum(resid ** 2)), "n": n}


def _as_id(p):
    """Accept 3, '3', 'P3', 'p3' -> 'P3'."""
    if isinstance(p, str):
        return "P" + p.upper().lstrip("P")
    return f"P{int(p)}"


# =============================================================================
#  MAIN CLASS
# =============================================================================
class ModifiedScherrer:
    """Crystal size from an XRD pattern via the Modified Scherrer method."""

    def __init__(
        self,
        xy_file,
        wavelength=0.15405,
        K=0.89,
        instrumental_fwhm=0.0,
        two_theta_min=10.0,
        two_theta_max=90.0,
        dry_run=False,
        use_peaks=None,
        exclude_peaks=(),
        lock_peaks=(),
        prominence_frac=0.02,
        min_distance_deg=0.30,
        n_peaks=12,
        min_intensity=None,
        profile="pseudo_voigt",
        fit_window_factor=3.0,
        min_fit_r2=0.80,
        prune_outliers=True,
        min_peaks_kept=5,
        slope_tolerance=0.15,
        paper_rad_factor=False,
        label="",
        output_dir=None,
        plot=("pattern", "scherrer"),
        verbose=True,
    ):
        self.xy_file = xy_file
        self.wavelength, self.K = wavelength, K
        self.instrumental_fwhm = instrumental_fwhm
        self.tt_min, self.tt_max = two_theta_min, two_theta_max
        self.dry_run = dry_run
        self.use_peaks = use_peaks
        self.exclude_peaks = exclude_peaks or ()
        self.lock_peaks = lock_peaks or ()
        self.prominence_frac, self.min_distance_deg = prominence_frac, min_distance_deg
        self.n_peaks, self.min_intensity = n_peaks, min_intensity
        self.profile, self.fit_window_factor = profile, fit_window_factor
        self.min_fit_r2 = min_fit_r2
        self.prune = prune_outliers
        self.min_peaks_kept, self.slope_tolerance = min_peaks_kept, slope_tolerance
        self.deg2rad = 0.0174 if paper_rad_factor else np.pi / 180
        self.label = label
        self.output_dir = output_dir
        self.plot = [p for p in (plot or []) if p]
        self.verbose = verbose
        self._log_lines = []
        self._stem = None
        self.results = {}

    # ---------------------------------------------------------------- output
    def _p(self, text=""):
        self._log_lines.append(str(text))
        if self.verbose:
            print(text)

    def _hr(self, title=""):
        self._p("\n" + "=" * 78)
        if title:
            self._p(title)
            self._p("=" * 78)

    # ------------------------------------------------------------ steps 1, 2
    def load(self):
        rows = []
        with open(self.xy_file, "r", errors="ignore") as fh:
            for line in fh:
                line = line.strip().replace(",", " ")
                if not line or line[0] in "#!;'\"" or line[0].isalpha():
                    continue
                parts = line.split()
                try:
                    rows.append((float(parts[0]), float(parts[1])))
                except (ValueError, IndexError):
                    continue
        if not rows:
            raise ValueError(f"No numeric data found in {self.xy_file}")
        data = np.array(rows)
        m = (data[:, 0] >= self.tt_min) & (data[:, 0] <= self.tt_max)
        self.tt, self.raw = data[m, 0], data[m, 1]

        self._hr("STEP 1  -  LOAD PATTERN")
        self._p(f"  file          : {self.xy_file}")
        self._p(f"  points        : {len(self.tt)}")
        self._p(f"  2theta range  : {self.tt.min():.3f} to {self.tt.max():.3f} deg")
        self._p(f"  step size     : {np.median(np.diff(self.tt)):.4f} deg")
        self._p(f"  max intensity : {self.raw.max():.0f} counts")
        self._p(f"  wavelength    : {self.wavelength} nm,  K = {self.K}")
        if self.instrumental_fwhm > 0:
            self._p(f"  instrumental FWHM: {self.instrumental_fwhm} deg (deconvoluted)")

        n = len(self.raw)
        w = min(101 if n > 101 else (n // 2) * 2 + 1, n if n % 2 else n - 1)
        half = w // 2
        pad = np.pad(self.raw, half, mode="edge")
        rmin = np.array([pad[i:i + w].min() for i in range(n)])
        self.bkg = np.convolve(np.pad(rmin, half, mode="edge"),
                               np.ones(w) / w, mode="valid")[:n]
        self.net = self.raw - self.bkg

        self._hr("STEP 2  -  BACKGROUND SUBTRACTION")
        self._p(f"  mean background : {self.bkg.mean():.1f} counts")
        self._p(f"  max net signal  : {self.net.max():.0f} counts")

    # ---------------------------------------------------------------- step 3
    def detect(self):
        """Find every peak and give it a permanent ID, numbered by 2theta."""
        step = np.median(np.diff(self.tt))
        idx, props = find_peaks(
            self.net,
            prominence=self.prominence_frac * self.net.max(),
            distance=max(1, int(round(self.min_distance_deg / step))),
            width=1,
        )
        order = np.argsort(self.tt[idx])
        self.peaks = []
        for rank, j in enumerate(order, 1):
            i = idx[j]
            self.peaks.append({
                "id": f"P{rank}",
                "two_theta_guess": float(self.tt[i]),
                "height": float(self.net[i]),
                "prominence": float(props["prominences"][j]),
                "rough_fwhm": float(props["widths"][j] * step),
            })
        self._hr("STEP 3  -  PEAK DETECTION")
        self._p(f"  prominence threshold : "
                f"{self.prominence_frac * self.net.max():.1f} counts "
                f"({self.prominence_frac * 100:.1f} % of max)")
        self._p(f"  minimum separation   : {self.min_distance_deg} deg")
        self._p(f"  peaks found          : {len(self.peaks)}  "
                f"(IDs P1..P{len(self.peaks)}, numbered by 2theta)")
        self._p("\n  Raise prominence_frac to ignore noise, lower it to catch weak peaks.")

    # ---------------------------------------------------------------- step 4
    def fit_all_peaks(self):
        """Fit a profile to every detected peak and print the inventory."""
        model, n_par = _profile_model(self.profile)
        step = np.median(np.diff(self.tt))
        self._hr("STEP 4  -  PEAK INVENTORY (profile fit of every peak)")
        self._p(f"  profile: {self.profile} + linear background")
        self._p(f"\n{'ID':>5} {'2theta':>9} {'height':>9} {'rel %':>7} "
                f"{'FWHM deg':>10} {'+/-':>9} {'fit R^2':>9}  note")
        self._p("-" * 78)

        imax = max(p["height"] for p in self.peaks)
        for p in self.peaks:
            half = max(self.fit_window_factor * p["rough_fwhm"], 3 * step)
            m = ((self.tt >= p["two_theta_guess"] - half) &
                 (self.tt <= p["two_theta_guess"] + half))
            x, y = self.tt[m], self.net[m]
            p["fit_ok"], p["note"] = False, ""
            if len(x) < n_par + 2:
                p["note"] = "too few points"
            else:
                p0 = [p["height"], p["two_theta_guess"], p["rough_fwhm"]]
                lo = [0.0, x.min(), 1e-4]
                hi = [np.inf, x.max(), x.max() - x.min()]
                if self.profile == "pseudo_voigt":
                    p0, lo, hi = p0 + [0.5], lo + [0.0], hi + [1.0]
                p0 += [0.0, float(np.median(y))]
                lo += [-np.inf, -np.inf]
                hi += [np.inf, np.inf]
                try:
                    popt, pcov = curve_fit(model, x, y, p0=p0, bounds=(lo, hi),
                                           maxfev=20000)
                    perr = (np.sqrt(np.diag(pcov)) if np.all(np.isfinite(pcov))
                            else np.full(len(popt), np.nan))
                    resid = y - model(x, *popt)
                    sst = np.sum((y - y.mean()) ** 2)
                    p.update({"two_theta": popt[1], "fwhm_deg": popt[2],
                              "fwhm_err_deg": perr[2], "popt": popt, "model": model,
                              "window": (x.min(), x.max()), "n_points": len(x),
                              "r2": 1 - np.sum(resid ** 2) / sst if sst > 0 else np.nan,
                              "fit_ok": True})
                    if self.min_fit_r2 > 0 and not (p["r2"] >= self.min_fit_r2):
                        p["note"] = f"poor fit (R2 < {self.min_fit_r2})"
                except (RuntimeError, ValueError):
                    p["note"] = "fit failed"

            rel = 100 * p["height"] / imax
            if p["fit_ok"]:
                self._p(f"{p['id']:>5} {p['two_theta']:>9.3f} {p['height']:>9.0f} "
                        f"{rel:>7.1f} {p['fwhm_deg']:>10.4f} {p['fwhm_err_deg']:>9.4f} "
                        f"{p['r2']:>9.4f}  {p['note']}")
            else:
                self._p(f"{p['id']:>5} {p['two_theta_guess']:>9.3f} {p['height']:>9.0f} "
                        f"{rel:>7.1f} {'-':>10} {'-':>9} {'-':>9}  {p['note']}")

        good = [p for p in self.peaks if p["fit_ok"] and not p["note"]]
        self._p(f"\n  {len(good)} of {len(self.peaks)} peaks fitted cleanly.")
        self._p("\n  Copy the IDs of the peaks belonging to your phase into use_peaks, e.g."
                "\n      use_peaks = ["
                + ", ".join(f'"{p["id"]}"' for p in good[:6])
                + ("" if len(good) <= 6 else ", ...") + "]")

    # ---------------------------------------------------------------- step 5
    def select(self):
        self._hr("STEP 5  -  PEAK SELECTION")
        by_id = {p["id"]: p for p in self.peaks}

        if self.use_peaks is not None:
            wanted = [_as_id(p) for p in self.use_peaks]
            unknown = [w for w in wanted if w not in by_id]
            if unknown:
                raise ValueError(
                    f"Unknown peak ID(s): {', '.join(unknown)}. "
                    f"Available: P1..P{len(self.peaks)}. Rerun with dry_run=True "
                    f"if the detection settings changed - IDs are renumbered.")
            sel = [by_id[w] for w in wanted]
            self._p(f"  MANUAL selection: {len(sel)} peaks requested")
            self._p("    " + ", ".join(f"{p['id']}({p['two_theta_guess']:.2f})"
                                       for p in sel))
            bad = [p for p in sel if not p["fit_ok"]]
            if bad:
                self._p("  dropped, no usable profile fit: "
                        + ", ".join(f"{p['id']} [{p['note']}]" for p in bad))
                sel = [p for p in sel if p["fit_ok"]]
            poor = [p for p in sel if p["note"]]
            if poor:
                self._p("  kept despite a poor fit (you asked for them explicitly): "
                        + ", ".join(p["id"] for p in poor))
        else:
            sel = [p for p in self.peaks if p["fit_ok"] and not p["note"]]
            self._p(f"  AUTOMATIC selection: {len(sel)} cleanly fitted peaks")
            sel = sorted(sel, key=lambda p: -p["height"])
            if self.min_intensity is not None:
                before = len(sel)
                sel = [p for p in sel if p["height"] >= self.min_intensity]
                self._p(f"    min_intensity = {self.min_intensity} -> "
                        f"{len(sel)} of {before} kept")
            if self.n_peaks is not None:
                before = len(sel)
                sel = sel[:self.n_peaks]
                self._p(f"    n_peaks = {self.n_peaks} -> {len(sel)} of {before} kept")

        if self.exclude_peaks:
            drop = {_as_id(p) for p in self.exclude_peaks}
            before = len(sel)
            sel = [p for p in sel if p["id"] not in drop]
            self._p(f"  exclude_peaks {sorted(drop)} -> {len(sel)} of {before} kept")

        self.locked = {_as_id(p) for p in self.lock_peaks}
        if self.locked:
            self._p(f"  lock_peaks {sorted(self.locked)}: these will never be pruned")

        self.selected = sorted(sel, key=lambda p: p["two_theta"])
        self._p(f"\n  going into the fit: {len(self.selected)} peaks")
        self._p("  " + ", ".join(f"{p['id']}({p['two_theta']:.2f})"
                                 for p in self.selected))
        if len(self.selected) < 2:
            raise ValueError("Fewer than 2 usable peaks - loosen the filters.")
        if len(self.selected) < self.min_peaks_kept:
            self._p(f"\n  NOTE: fewer than {self.min_peaks_kept} peaks. Per the paper the "
                    f"slope is then acceptable if it stays below 10.")

    # ------------------------------------------------------------- steps 6, 7
    def build_table(self):
        self.rows = []
        for p in self.selected:
            beta_deg = p["fwhm_deg"]
            if self.instrumental_fwhm > 0:
                corr = beta_deg ** 2 - self.instrumental_fwhm ** 2
                if corr <= 0:
                    self._p(f"  {p['id']} is narrower than the instrument - dropped")
                    continue
                beta_deg = np.sqrt(corr)
            th = np.radians(p["two_theta"] / 2)
            beta_rad = beta_deg * self.deg2rad
            self.rows.append({
                "id": p["id"], "two_theta": p["two_theta"], "fwhm_deg": p["fwhm_deg"],
                "beta_deg_corr": beta_deg, "theta_deg": p["two_theta"] / 2,
                "beta_rad": beta_rad, "ln_beta": np.log(beta_rad),
                "cos_theta": np.cos(th), "inv_cos": 1 / np.cos(th),
                "x": np.log(1 / np.cos(th)), "height": p["height"], "r2": p["r2"],
            })

        self._hr("STEP 6  -  Ln(beta) vs Ln(1/cos theta) TABLE")
        self._p(f"  deg -> rad factor: {self.deg2rad:.6f}"
                + ("  (paper rounds to 0.0174)"
                   if abs(self.deg2rad - 0.0174) > 1e-6 else ""))
        self._peak_table(self.rows, "Equivalent of Tables 1-3 in the paper")

        self._hr("STEP 7  -  PLAIN SCHERRER PER PEAK (comparison only)")
        self._p(f"{'ID':>5} {'2theta':>9} {'L_Scherrer nm':>15}")
        self._p("-" * 32)
        for r in self.rows:
            L_i = self.K * self.wavelength / (r["beta_rad"] * r["cos_theta"])
            self._p(f"{r['id']:>5} {r['two_theta']:>9.3f} {L_i:>15.2f}")
        self._p("\n  The spread here is the problem the modified method fixes: one crystal"
                "\n  size cannot reproduce every peak individually.")

    def _peak_table(self, rows, title):
        self._p(f"\n{title}")
        self._p("-" * 112)
        self._p(f"{'ID':>5} {'2theta':>9} {'FWHM deg':>10} {'theta':>9} "
                f"{'beta rad':>11} {'ln beta':>10} {'cos th':>9} {'1/cos th':>9} "
                f"{'ln(1/cos)':>10} {'I':>9}")
        self._p("-" * 112)
        for r in rows:
            self._p(f"{r['id']:>5} {r['two_theta']:>9.3f} {r['fwhm_deg']:>10.4f} "
                    f"{r['theta_deg']:>9.4f} {r['beta_rad']:>11.5f} "
                    f"{r['ln_beta']:>10.5f} {r['cos_theta']:>9.5f} {r['inv_cos']:>9.5f} "
                    f"{r['x']:>10.5f} {r['height']:>9.0f}")
        self._p("-" * 112)

    # ------------------------------------------------------------ steps 8, 9
    def _size(self, fit):
        kl = self.K * self.wavelength
        exp_int = np.exp(fit["intercept"])
        L = kl / exp_int
        L_err = L * fit["intercept_err"] if np.isfinite(fit["intercept_err"]) else np.nan
        return L, L_err, exp_int

    def regress(self):
        self._hr("STEP 8  -  LINEAR FIT WITH ALL SELECTED PEAKS")
        self.fit_all = linear_fit([r["x"] for r in self.rows],
                                  [r["ln_beta"] for r in self.rows])
        self._print_fit(self.fit_all, "Fit using every selected peak")
        L0, L0e, _ = self._size(self.fit_all)
        self._p(f"    -> L = {L0:.2f} +/- {L0e:.2f} nm  (before outlier removal)")
        d = abs(self.fit_all["slope"] - 1)
        self._p(f"\n  Rule 1: |slope - 1| = {d:.4f} -> "
                f"{'acceptable, nothing to prune' if d <= self.slope_tolerance else 'too far, pruning'}")

        self._hr(f"STEP 9  -  OUTLIER REMOVAL (slope -> 1, floor of "
                 f"{self.min_peaks_kept} peaks)")
        kept, fit = list(self.rows), self.fit_all
        log = [(0, [], fit)]
        if not self.prune:
            self._p("  prune_outliers = False - the fit above is used as it stands.")
        else:
            while (abs(fit["slope"] - 1) > self.slope_tolerance
                   and len(kept) > self.min_peaks_kept):
                best = None
                for i, cand in enumerate(kept):
                    if cand["id"] in self.locked:
                        continue
                    trial = kept[:i] + kept[i + 1:]
                    tf = linear_fit([r["x"] for r in trial],
                                    [r["ln_beta"] for r in trial])
                    sc = abs(tf["slope"] - 1)
                    if best is None or sc < best[0]:
                        best = (sc, tf, trial, cand["id"])
                if best is None or best[0] >= abs(fit["slope"] - 1) - 1e-12:
                    self._p("  no further removal brings the slope closer to 1 - stopping.")
                    break
                _, fit, kept, _ = best
                kept_ids = {r["id"] for r in kept}
                dropped = [r["id"] for r in self.rows if r["id"] not in kept_ids]
                log.append((len(log), dropped, fit))

            self._p(f"{'step':>5} {'n':>4} {'slope':>10} {'intercept':>11} {'R^2':>8} "
                    f"{'L nm':>9}   removed so far")
            self._p("-" * 90)
            for step, dropped, f in log:
                Ls, _, _ = self._size(f)
                self._p(f"{step:>5} {f['n']:>4} {f['slope']:>10.5f} "
                        f"{f['intercept']:>11.5f} {f['r2']:>8.4f} {Ls:>9.2f}   "
                        + ("-" if not dropped else ", ".join(dropped)))
            self._p(f"\n  {len(self.rows) - len(kept)} peak(s) removed, {len(kept)} kept.")
            if len(kept) == self.min_peaks_kept and abs(fit["slope"] - 1) > self.slope_tolerance:
                self._p("  The floor of min_peaks_kept was reached before the slope "
                        "settled near 1.\n  Either the selection mixes phases, or the "
                        "broadening is not size alone (strain).")

        self.kept, self.fit_final = kept, fit
        self._peak_table(kept, "Final peak set used for the reported crystal size")

    def _print_fit(self, fit, label):
        self._p(f"\n  {label}")
        self._p("    y = a + b*x   (y = ln beta, x = ln(1/cos theta))")
        self._p(f"    slope     b = {fit['slope']:.5f} +/- {fit['slope_err']:.5f}")
        self._p(f"    intercept a = {fit['intercept']:.5f} +/- {fit['intercept_err']:.5f}")
        self._p(f"    R^2         = {fit['r2']:.5f}   residual SS = {fit['rss']:.5f}"
                f"   n = {fit['n']}")

    # --------------------------------------------------------------- step 10
    def report(self):
        self._hr("STEP 10  -  FINAL RESULT")
        self._print_fit(self.fit_final, "Final fit")
        L, L_err, exp_int = self._size(self.fit_final)
        kl = self.K * self.wavelength
        self._p(f"\n  exp(intercept) = exp({self.fit_final['intercept']:.5f}) "
                f"= {exp_int:.6f}")
        self._p(f"  K * lambda     = {self.K} * {self.wavelength} = {kl:.5f} nm")
        self._p(f"  L = K*lambda / exp(intercept) = {kl:.5f} / {exp_int:.6f}")
        if self.label:
            self._p(f"\n  SAMPLE / PHASE : {self.label}")
        self._p(f"\n  PEAKS USED     : "
                + ", ".join(f"{r['id']}({r['two_theta']:.2f})" for r in self.kept))
        self._p(f"  CRYSTAL SIZE L = {L:.2f} +/- {L_err:.2f} nm")
        self._p(f"  final slope    = {self.fit_final['slope']:.5f}")
        ok = abs(self.fit_final["slope"] - 1) <= self.slope_tolerance
        loose = len(self.kept) <= 5 and abs(self.fit_final["slope"]) < 10
        self._p("  rule check     : "
                + ("slope close to 1 - result is credible" if ok else
                   ("slope < 10 with <=5 peaks - acceptable per the paper" if loose else
                    "slope still far from 1 - treat L with caution")))
        self.results = {"L_nm": L, "L_err_nm": L_err, "slope": self.fit_final["slope"],
                        "intercept": self.fit_final["intercept"],
                        "peaks_used": [r["id"] for r in self.kept],
                        "peaks_removed": [r["id"] for r in self.rows
                                          if r not in self.kept],
                        "n_peaks_used": len(self.kept), "fit": self.fit_final,
                        "kept": self.kept, "all_rows": self.rows, "label": self.label}

    # ------------------------------------------------------------------ save
    def save(self, suffix=""):
        if not self.output_dir:
            return
        os.makedirs(self.output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(self.xy_file))[0]
        tag = f"_{self.label}" if self.label else ""
        stem = os.path.join(self.output_dir, f"{base}{tag}_modScherrer{suffix}")
        with open(stem + "_report.txt", "w") as fh:
            fh.write("\n".join(self._log_lines))
        self._p(f"\n  report -> {stem}_report.txt")
        if not self.dry_run:
            kept_ids = {r["id"] for r in self.kept}
            with open(stem + "_peaks.csv", "w") as fh:
                fh.write("id,two_theta,fwhm_deg,beta_rad,ln_beta,cos_theta,"
                         "ln_inv_cos,intensity,used_in_final_fit\n")
                for r in self.rows:
                    fh.write(f"{r['id']},{r['two_theta']:.4f},{r['fwhm_deg']:.5f},"
                             f"{r['beta_rad']:.6f},{r['ln_beta']:.5f},"
                             f"{r['cos_theta']:.5f},{r['x']:.5f},{r['height']:.0f},"
                             f"{int(r['id'] in kept_ids)}\n")
            self._p(f"  peaks  -> {stem}_peaks.csv")
        self._stem = stem

    # ----------------------------------------------------------------- plots
    def make_plots(self):
        if not self.plot:
            return
        import matplotlib.pyplot as plt

        self._hr("PLOTS")
        stem = self._stem
        kept_ids = {r["id"] for r in self.kept} if not self.dry_run else set()
        sel_ids = ({p["id"] for p in self.selected} if not self.dry_run
                   else {p["id"] for p in self.peaks})

        if "pattern" in self.plot:
            fig, ax = plt.subplots(figsize=(12, 5.5))
            ax.plot(self.tt, self.raw, lw=0.8, color="0.35", label="measured")
            ax.plot(self.tt, self.bkg, lw=1.0, color="tab:orange", label="background")
            top = self.raw.max()
            for p in self.peaks:
                tt_p = p.get("two_theta", p["two_theta_guess"])
                y_p = p["height"] + np.interp(tt_p, self.tt, self.bkg)
                if self.dry_run:
                    col = "tab:blue"
                elif p["id"] in kept_ids:
                    col = "tab:green"
                elif p["id"] in sel_ids:
                    col = "tab:red"
                else:
                    col = "0.7"
                ax.plot(tt_p, y_p, "v", color=col, ms=7)
                # stagger the labels; weak peaks often crowd together
                dy = 8 + 9 * (int(p["id"][1:]) % 3)
                ax.annotate(p["id"], (tt_p, y_p), textcoords="offset points",
                            xytext=(0, dy), ha="center", fontsize=7, color=col)
            ax.set_xlabel(r"2$\theta$, degree")
            ax.set_ylabel("Intensity, counts")
            ax.set_ylim(top=top * 1.15)
            title = ("Peak inventory - IDs to put into use_peaks" if self.dry_run else
                     "green = used in final fit, red = selected but pruned, "
                     "grey = not selected")
            ax.set_title(title + (f"   [{self.label}]" if self.label else ""))
            ax.legend(loc="upper right", fontsize=8)
            fig.tight_layout()
            if stem:
                fig.savefig(stem + "_pattern.png", dpi=150)
                self._p(f"  pattern plot -> {stem}_pattern.png")

        if "scherrer" in self.plot and not self.dry_run:
            fig, ax = plt.subplots(figsize=(7, 5.5))
            xa = [r["x"] for r in self.rows]
            ya = [r["ln_beta"] for r in self.rows]
            ax.scatter(xa, ya, facecolors="none", edgecolors="tab:red",
                       label=f"all selected (slope {self.fit_all['slope']:.4f})")
            ax.scatter([r["x"] for r in self.kept], [r["ln_beta"] for r in self.kept],
                       color="tab:green",
                       label=f"kept (slope {self.fit_final['slope']:.4f})")
            xs = np.linspace(min(xa) * 0.9, max(xa) * 1.05, 50)
            ax.plot(xs, self.fit_all["intercept"] + self.fit_all["slope"] * xs,
                    "r--", lw=1)
            ax.plot(xs, self.fit_final["intercept"] + self.fit_final["slope"] * xs,
                    "g-", lw=1.5)
            for r in self.rows:
                ax.annotate(r["id"], (r["x"], r["ln_beta"]),
                            textcoords="offset points", xytext=(5, 5), fontsize=7)
            L, Le, _ = self._size(self.fit_final)
            ax.set_xlabel(r"Ln $(1/\cos\theta)$")
            ax.set_ylabel(r"Ln $\beta$, radian")
            ax.set_title((f"{self.label}: " if self.label else "")
                         + f"L = {L:.2f} $\\pm$ {Le:.2f} nm")
            ax.legend(fontsize=8)
            fig.tight_layout()
            if stem:
                fig.savefig(stem + "_scherrer.png", dpi=150)
                self._p(f"  Scherrer plot -> {stem}_scherrer.png")

        if "fits" in self.plot:
            shown = [p for p in self.peaks
                     if p["fit_ok"] and (self.dry_run or p["id"] in sel_ids)]
            n = len(shown)
            ncol = 3
            nrow = max(1, int(np.ceil(n / ncol)))
            fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 2.7 * nrow),
                                     squeeze=False)
            flat = axes.ravel()
            for ax, p in zip(flat, shown):
                lo, hi = p["window"]
                m = (self.tt >= lo) & (self.tt <= hi)
                xs = np.linspace(lo, hi, 300)
                ax.plot(self.tt[m], self.net[m], "k.", ms=3)
                ax.plot(xs, p["model"](xs, *p["popt"]), "r-", lw=1.2)
                mark = (" [kept]" if p["id"] in kept_ids else
                        ("" if self.dry_run else " [pruned]"))
                ax.set_title(f"{p['id']}  {p['two_theta']:.2f} deg{mark}\n"
                             f"FWHM {p['fwhm_deg']:.4f} deg, R2 {p['r2']:.3f}",
                             fontsize=8)
                ax.tick_params(labelsize=7)
            for ax in flat[n:]:
                ax.axis("off")
            fig.tight_layout()
            if stem:
                fig.savefig(stem + "_peakfits.png", dpi=150)
                self._p(f"  peak fits plot -> {stem}_peakfits.png")

        if self.verbose:
            plt.show()

    # ------------------------------------------------------------------- run
    def run(self):
        self._log_lines = []
        self.load()
        self.detect()
        self.fit_all_peaks()
        if self.dry_run:
            self._hr("DRY RUN - stopping after the inventory")
            self._p("  No crystal size calculated. Put the IDs you want into use_peaks")
            self._p("  and set dry_run = False, or leave use_peaks = None to let the")
            self._p("  script pick the most intense peaks by itself.")
            self.kept, self.rows, self.selected = [], [], []
            self.save(suffix="_inventory")
            self.make_plots()
            return {"peaks": self.peaks}
        self.select()
        self.build_table()
        self.regress()
        self.report()
        self.save()
        self.make_plots()
        return self.results


# =============================================================================
#  Self test: reproduces the published Fe2O3 fit from Table 1 of the paper
# =============================================================================
def self_test():
    x = [0.03438, 0.04801, 0.05268, 0.07170, 0.10657, 0.11214,
         0.12805, 0.15604, 0.20472, 0.22377, 0.23075, 0.25839]
    y = [-5.13009, -5.15090, -5.19072, -4.99289, -6.57701, -5.13009,
         -5.32425, -5.13896, -4.80631, -4.78525, -5.15995, -4.96758]
    f = linear_fit(x, y)
    L = 0.89 * 0.15405 / np.exp(f["intercept"])
    print("=" * 78)
    print("SELF TEST - Fe2O3 data from Table 1 of the paper")
    print("=" * 78)
    print(f"  slope     = {f['slope']:.5f}   paper: 1.65023")
    print(f"  intercept = {f['intercept']:.5f}   paper: -5.41994")
    print(f"  int. err  = {f['intercept_err']:.5f}   paper: 0.27791")
    print(f"  R^2       = {f['r2']:.5f}   paper: 0.07804")
    print(f"  L         = {L:.2f} nm   paper: 30.94 nm")
    print("\n  Error bars: the paper quotes '30.94 +/- 0.27 nm', which is the intercept")
    print("  uncertainty copied across as if it were nanometres. Propagated properly,")
    print(f"  dL = L * d(intercept) = {L * f['intercept_err']:.2f} nm, which is what this")
    print("  script reports. Expect larger error bars than the publication.")
    ok = abs(f["slope"] - 1.65023) < 1e-4 and abs(f["intercept"] + 5.41994) < 1e-4
    print(f"\n  {'PASS - the algebra matches the publication' if ok else 'FAIL'}")


# =============================================================================
#  Convenience entry point - run directly:  python modified_scherrer.py
#  Or paste/edit the block below into a Spyder cell and press Ctrl+Enter.
# =============================================================================

if __name__ == "__main__":

    m = ModifiedScherrer(
        xy_file            = r"O2_5sccm_A_435C_glass.xy",   # << your pattern file
        label              = "SnO",     # free text, goes into the output file names
        # ── Instrument ────────────────────────────────────────────────
        wavelength         = 0.15405,   # nm -> Cu Ka1. Cu Ka average = 0.15418
        K                  = 0.89,      # Scherrer shape factor used in the paper
        instrumental_fwhm  = 0.0,       # deg -> from a LaB6/Si standard, e.g. 0.08
        two_theta_min      = 10.0,
        two_theta_max      = 90.0,
        # ── Peak detection (run 1: every peak gets an ID, P1, P2, ...) ─
        dry_run            = False,     # << True = only detect, fit and list the
                                        #    peaks with their IDs, then stop
        prominence_frac    = 0.02,      # threshold as a fraction of max intensity
        min_distance_deg   = 0.30,      # deg -> minimum peak separation
        # ── Which peaks to use (run 2) ────────────────────────────────
        #   MANUAL : use_peaks = ["P10", "P23", "P28", "P34", "P38", "P40", "P42"]
        #            (IDs come from the dry run; plain numbers like [10, 23] work too)
        #   AUTO   : use_peaks = None -> take the cleanly fitted peaks, strongest
        #            first, limited by min_intensity and n_peaks below
        use_peaks          = None,
        exclude_peaks      = [],        # IDs to drop from whatever was selected
        lock_peaks         = [],        # IDs the outlier pruning may never remove
        n_peaks            = 12,        # AUTO only: keep the N most intense
        min_intensity      = None,      # AUTO only: net-height cutoff in counts
        # ── Profile fitting ───────────────────────────────────────────
        profile            = "pseudo_voigt",  # "pseudo_voigt"|"gaussian"|"lorentzian"
        fit_window_factor  = 3.0,       # window half width = factor * rough FWHM
        min_fit_r2         = 0.80,      # flags bad profile fits. 0 = accept everything
        # ── Modified Scherrer rules ───────────────────────────────────
        prune_outliers     = True,      # False = fit exactly the peaks you gave
        min_peaks_kept     = 5,         # never prune below this many peaks
        slope_tolerance    = 0.15,      # stop pruning once |slope - 1| < this
        paper_rad_factor   = False,     # True reproduces the paper's rounded 0.0174
        # ── Output ────────────────────────────────────────────────────
        output_dir         = r".",      # folder for report .txt, .csv and .png
        # Choose any combination of the three plot types, or None to skip.
        #   "pattern"  – measured pattern with every peak marked and labelled
        #   "fits"     – the profile fits, so you can check each FWHM
        #   "scherrer" – the Ln beta vs Ln(1/cos theta) plot
        plot = ["pattern", "scherrer", "fits"],
        verbose            = True,
    )

    res = m.run()

    # res is a dict: L_nm, L_err_nm, slope, intercept, peaks_used, peaks_removed, ...
    # A second phase in the same pattern is just a second peak list:
    #   m.use_peaks = ["P21", "P29", "P33", "P37", "P41"]
    #   m.label     = "SnO2"
    #   res2 = m.run()

    # self_test()   # <- uncomment to check the algebra against the publication
