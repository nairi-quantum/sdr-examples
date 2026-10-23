# -*- coding: utf-8 -*-
"""Experiment 1 - Excess-noise eavesdropping detection: software baseline (simulation).

Pure-NumPy reproduction of Lilit's GNU Radio software baseline (no USRP). It mirrors
the flowgraph in this folder's README:

  Alice  s = X + jP,  X,P ~ N(0, V_A)         (complex Gaussian, V_A per quadrature)
  Channel noise  n0,  variance N0 per quadrature
  Eve (optional) nE,  excess noise xi_E per quadrature
  Bob  y = s + n0 (+ nE)

The receiver estimates the excess noise from the residual r = y - s (Alice's symbols are
known in this software baseline):

  xi_hat = mean(|r|^2)/2 - N0

and raises an alarm when xi_hat exceeds the threshold set by the false-alarm probability:

  xi_th = Qinv(P_fa) / sqrt(M)

This script prints the same quantities Lilit measured, runs a Monte-Carlo estimate of the
detection probability P_d (the step a single GNU Radio run cannot give you), and saves a
4-panel figure. Pure numpy + matplotlib, no hardware, no scipy.
"""
import os
import numpy as np
from math import erfc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY = "#002070"; BLUE = "#2050D0"; ORANGE = "#F08010"; RED = "#D01010"; GREEN = "#1e9e6a"; GREY = "#5a5f6e"

# ---------- Q function and its inverse (no scipy) ----------
def Q(x):
    """Right-tail of the standard normal, elementwise."""
    x = np.asarray(x, dtype=float)
    return 0.5 * np.vectorize(erfc)(x / np.sqrt(2.0))

def Qinv(p):
    """Inverse of Q by bisection (Q is monotone decreasing)."""
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if float(Q(mid)) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

# ---------- parameters (match the README / Lilit's settings) ----------
V_A   = 5.0        # Alice variance per quadrature
N0    = 1.0        # channel (shot-noise) variance per quadrature  -> normalisation baseline
M     = 100_000    # samples
P_FA  = 0.01       # target false-alarm probability
P_D   = 0.90       # target detection probability
rng   = np.random.default_rng(12345)

def make_signals(xi_E, M, rng):
    """Return Alice s and Bob y with independent Gaussian draws (independent 'seeds')."""
    s  = rng.normal(0, np.sqrt(V_A), M) + 1j * rng.normal(0, np.sqrt(V_A), M)
    n0 = rng.normal(0, np.sqrt(N0), M) + 1j * rng.normal(0, np.sqrt(N0), M)
    y  = s + n0
    if xi_E > 0:
        nE = rng.normal(0, np.sqrt(xi_E), M) + 1j * rng.normal(0, np.sqrt(xi_E), M)
        y = y + nE
    return s, y

def estimate_xi(s, y, N0=1.0):
    r = y - s
    return np.mean(np.abs(r) ** 2) / 2.0 - N0, np.var(r.real), np.var(r.imag)

xi_th = Qinv(P_FA) / np.sqrt(M)

# ---------- run the two cases Lilit reported ----------
print("=" * 60)
print("Experiment 1 - excess-noise detection, software baseline")
print(f"V_A={V_A}  N0={N0}  M={M}  P_fa={P_FA}  threshold xi_th={xi_th:.5f}")
print("=" * 60)
results = {}
for label, xi_E in [("No Eve", 0.0), ("Eve (xi_E=0.1)", 0.1)]:
    s, y = make_signals(xi_E, M, rng)
    xi_hat, vI, vQ = estimate_xi(s, y, N0)
    decision = "ALARM" if xi_hat > xi_th else "No alarm"
    results[label] = (xi_E, xi_hat, vI, vQ, decision)
    print(f"{label:16s}  I-var={vI:.4f}  Q-var={vQ:.4f}  "
          f"xi_hat={xi_hat:+.5f}  -> {decision}")

# ---------- required M for 90% detection (closed form) ----------
qfa, qd = Qinv(P_FA), Qinv(P_D)   # 2.326, -1.282
print("-" * 60)
print("Samples M needed for P_d = 0.90  (M = [ (Qinv(Pfa) - (1+xi)Qinv(Pd)) / xi ]^2):")
need = {}
for xi_E in (0.10, 0.02, 0.01):
    Mreq = ((qfa - (1 + xi_E) * qd) / xi_E) ** 2
    need[xi_E] = Mreq
    print(f"  xi_E={xi_E:<5}  ->  M ~ {Mreq:,.0f}")
print(f"(Our M={M:,} is enough for xi_E=0.1 and 0.02; xi_E=0.01 needs ~{need[0.01]:,.0f}.)")

# ---------- Monte-Carlo detection probability (the multi-run check) ----------
def mc_pd(xi_E, M, trials, rng):
    xth = Qinv(P_FA) / np.sqrt(M)   # threshold is M-specific
    alarms = 0
    for _ in range(trials):
        s, y = make_signals(xi_E, M, rng)
        xi_hat, _, _ = estimate_xi(s, y, N0)
        alarms += (xi_hat > xth)
    return alarms / trials

print("-" * 60)
mc_rng = np.random.default_rng(2024)
for xi_E in (0.10, 0.02):
    pd_emp = mc_pd(xi_E, M, 300, mc_rng)
    pd_th = float(Q((qfa - xi_E * np.sqrt(M)) / (1 + xi_E)))
    print(f"P_d at M={M:,} xi_E={xi_E}: Monte-Carlo={pd_emp:.3f}  theory={pd_th:.3f}")

# ================= figure =================
plt.rcParams.update({"font.size": 10, "axes.titlesize": 11.5,
                     "axes.titlecolor": NAVY, "axes.titleweight": "bold"})
fig, ((a, b), (c, d)) = plt.subplots(2, 2, figsize=(12.6, 9.0))

# (a) estimated xi, no-Eve vs Eve, against threshold
labels = list(results.keys())
xis = [results[k][1] for k in labels]
cols = [GREEN, RED]
a.bar(labels, xis, 0.5, color=cols, alpha=0.85)
a.axhline(xi_th, color=ORANGE, ls="--", lw=2, label=f"threshold {xi_th:.4f}")
for i, v in enumerate(xis):
    a.text(i, v + 0.004, f"{v:+.4f}", ha="center", fontsize=9, color=NAVY)
a.set_title("(a) Estimated excess noise vs alarm threshold")
a.set_ylabel(r"$\hat{\xi}$"); a.legend(fontsize=9); a.grid(axis="y", alpha=0.25)

# (b) distribution of xi_hat under H0 / H1 (many short runs) with threshold
def xi_draws(xi_E, M, n, rng):
    out = np.empty(n)
    for i in range(n):
        s, y = make_signals(xi_E, M, rng)
        out[i], _, _ = estimate_xi(s, y, N0)
    return out
dr = np.random.default_rng(7)
h0 = xi_draws(0.0, M, 400, dr)
h1 = xi_draws(0.1, M, 400, dr)
b.hist(h0, bins=40, color=GREEN, alpha=0.6, label="H0: no Eve")
b.hist(h1, bins=40, color=RED, alpha=0.6, label="H1: Eve xi=0.1")
b.axvline(xi_th, color=ORANGE, ls="--", lw=2, label="threshold")
b.set_title(r"(b) $\hat{\xi}$ distribution ($M=10^5$, 400 runs each)")
b.set_xlabel(r"$\hat{\xi}$"); b.set_ylabel("count"); b.legend(fontsize=8.5)

# (c) P_d vs M, theory + Monte-Carlo, for two xi_E
Mgrid = np.unique(np.round(np.logspace(2.3, 5.4, 26)).astype(int))
for xi_E, col in [(0.10, BLUE), (0.02, ORANGE)]:
    pd_theory = Q((qfa - xi_E * np.sqrt(Mgrid)) / (1 + xi_E))
    c.semilogx(Mgrid, pd_theory, color=col, lw=2, label=f"theory, xi={xi_E}")
    mcg = np.random.default_rng(99)
    Msub = [m for m in Mgrid if m <= 200_000][::3]
    pdm = [mc_pd(xi_E, int(m), 120, mcg) for m in Msub]
    c.semilogx(Msub, pdm, "o", color=col, ms=4)
c.axhline(0.90, color=GREY, ls=":", lw=1.2)
c.set_title("(c) Detection probability vs number of samples")
c.set_xlabel("M (samples)"); c.set_ylabel(r"$P_d$")
c.set_ylim(0, 1.03); c.grid(alpha=0.25, which="both"); c.legend(fontsize=8.5, loc="lower right")

# (d) required M table
d.axis("off")
d.set_title("(d) Samples needed for $P_d=0.90$")
rows = [("xi_E", "M (approx)")] + [(f"{x:g}", f"{need[x]:,.0f}") for x in (0.10, 0.02, 0.01)]
tbl = d.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="center")
tbl.auto_set_font_size(False); tbl.set_fontsize(11); tbl.scale(1, 1.8)
d.text(0.5, 0.12, f"operating points at P_fa=0.01; our run used M={M:,}",
       ha="center", transform=d.transAxes, fontsize=9, color=GREY)

fig.suptitle("Experiment 1: excess-noise eavesdropping detection - software baseline (no USRP)",
             fontsize=12.5, color=NAVY, weight="bold", y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.965))
out = os.path.join(HERE, "eavesdrop_baseline_sim.png")
fig.savefig(out, dpi=140, bbox_inches="tight")
print("-" * 60)
print("saved", os.path.basename(out))
