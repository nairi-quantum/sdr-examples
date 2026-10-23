# 07 — Excess-noise eavesdropping detection (Experiment 1)

Our first real QSDC-adjacent experiment: detect an eavesdropper (Eve) on a coherent-state
link from the **excess noise** she adds, using a software GNU Radio flowgraph **before any
USRP is involved**. Built and documented by **Lilit Gevorgyan**; this README is the English
companion to her original step-by-step walkthrough (in Armenian).

Alice sends a complex Gaussian signal `s = X + jP`; the channel adds baseline noise `n0`;
Eve (optionally) adds independent excess noise `nE`. Bob receives `y = s + n0 (+ nE)` and
estimates the excess noise `xi`. If `xi` exceeds a false-alarm threshold, the link raises an
alarm. Reproduce this in software first, then swap the file sources for the USRP blocks.

## Run (no hardware)
```bash
python -m pip install numpy matplotlib
python 07_eavesdrop_detection/eavesdrop_baseline_sim.py   # -> eavesdrop_baseline_sim.png
```
This pure-NumPy script reproduces Lilit's measurements, adds a Monte-Carlo detection-
probability check (what a single GNU Radio run cannot give you), and saves a 4-panel figure.

## The GNU Radio flowgraph (`01_software_baseline.grc`)
Build these blocks in GNU Radio Companion. GNU Radio's complex Gaussian **Noise Source**
splits its `Amplitude` across I and Q, so **variance per quadrature = Amplitude² / 2**, i.e.
`Amplitude = sqrt(2 * variance)`. (Confirm by measuring the I/Q variances — do not trust the
convention blindly; it is version-dependent.)

| Block | Setting | Why |
|---|---|---|
| Variable | `samp_rate = 32k` | stream rate |
| Noise Source (Alice) | Complex, Gaussian, **Amplitude 3.1623** = √(2·5), **Seed 11** | `s`, variance `V_A = 5` per quadrature |
| Noise Source (channel) | Complex, Gaussian, **Amplitude 1.4142** = √2, **Seed 22** | `n0`, variance `N0 = 1` per quadrature (normalisation) |
| Noise Source (Eve) | Complex, Gaussian, **Amplitude 0.4472** = √(2·0.1), **Seed 33** | `nE`, excess noise `xi_E = 0.1` per quadrature |
| Add | `y = s + n0 + nE` | Bob's received signal |
| Head | `Num Items = 100000` | capture M = 100,000 samples |
| File Sink ×2 | `alice_s.dat`, `bob_y.dat` (complex64) | save `s` and `y` |
| QT GUI Constellation Sink | — | watch the cloud widen when Eve is on |

> **Independent seeds matter.** If several Noise Sources share `Seed = 0` they emit the
> *same* sequence, the noises become correlated, and the estimate is biased. Use different
> seeds (11, 22, 33).

Then estimate `xi` from the saved captures:
```bash
python 07_eavesdrop_detection/estimate_baseline.py   # reads alice_s.dat / bob_y.dat
```

## The math (what the script and estimator implement)
- **Estimator:** `xi_hat = mean(|y - s|²) / 2 − N0`  (Bob knows `s` in this software baseline).
- **Alarm threshold** for false-alarm probability `P_fa`: `xi_th = Qinv(P_fa) / sqrt(M)`.
  For `P_fa = 0.01`, `M = 100000`: `xi_th ≈ 0.00736`.
- **Samples for 90% detection:** `M = [ (Qinv(P_fa) − (1+xi_E)·Qinv(P_d)) / xi_E ]²`.

| xi_E | M for P_d = 0.90 |
|---|---|
| 0.10 | ~1,400 |
| 0.02 | ~33,000 |
| 0.01 | ~131,000 |

So `M = 100,000` is comfortably enough for `xi_E = 0.1` and `0.02`; `xi_E = 0.01` needs more.

## Expected output
- **No Eve:** I/Q variances ≈ 1.00, `xi_hat ≈ 0` (< threshold) → **No alarm**.
- **Eve (xi_E = 0.1):** I/Q variances ≈ 1.10, `xi_hat ≈ 0.10` (> threshold) → **ALARM**.
- The Monte-Carlo `P_d` matches the theory curve, confirming the operating points.

## Toward the USRP (next step)
Replace the two File Sinks / sources with the radio blocks: host **Alice-TX and Bob-RX on the
USRP-2901** (two channels, shared clock) and run **Eve on the B206mini-i**. On real hardware
Bob will not have Alice's exact `s`, so `xi` is estimated from a disclosed subset of symbols
and the baseline `N0` is recalibrated against the measured hardware noise floor. The
software-baseline numbers above are the reference the hardware run is checked against.

## Files
- `eavesdrop_baseline_sim.py` — pure-NumPy reproduction + Monte-Carlo `P_d` (runs today).
- `estimate_baseline.py` — Lilit's estimator for real GNU Radio `.dat` captures.
- *(to add)* `01_software_baseline.grc` — Lilit's flowgraph, and her original walkthrough PDF.

Builds on the project's analytical model (Lilit's eavesdropping-detection paper) and shares
the Alice/Bob/Eve testbed with Martin's SDR work. Pure `numpy` + `matplotlib`, no external data.
