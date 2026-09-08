#!/usr/bin/env python3
"""06 - QSDC classical coordination channel (pure NumPy, runnable now).

Instead of a plain AWGN channel (example 02), this models the *classical*
coordination channel that a DL04-style QSDC session depends on, and reproduces the
analytical model from Nathalie's paper:

  Session structure: N_c = 3 legs (Bob->Alice->Bob).
  Per leg the control packet is lost with prob p and retransmitted up to r times.

  Throughput:   R(p)  = R0 * (1 - p^(r+1))^3
  Latency:      L(p)  = 3 * [ p*(1 - p^r)/(1 - p) * To + d ]
  Corruption / false-abort (undetected-vs-abort), two checks:
                F(pc) = 1 - (1 - pc)^2       (prob a session falsely aborts)
                R(pc) = R0 * (1 - pc)^2      (surviving throughput)

We Monte-Carlo the channel and overlay the closed forms. Dashed = analytical.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(2025)

# ---- parameters ----
R0   = 1.0        # normalized ideal throughput
Nc   = 3          # legs per session (DL04 two-leg -> 3 control exchanges)
r    = 2          # max retransmissions per leg
To   = 1.0        # timeout cost per failed attempt (normalized time units)
d    = 0.5        # base per-leg delay
jit  = 0.1        # jitter std-dev (half-normal-ish)
N    = 40_000     # Monte-Carlo sessions per point
p_grid  = np.linspace(0.0, 0.6, 13)
pc_grid = np.linspace(0.0, 0.3, 13)

def sim_leg_loss(p):
    """Return (success:bool, n_failed_attempts:int) for one leg with up to r retx."""
    failed = 0
    for attempt in range(r + 1):
        if rng.random() > p:          # delivered
            return True, failed
        failed += 1
    return False, failed              # all r+1 attempts lost -> leg fails

# ---- Monte-Carlo: throughput & latency vs packet loss p ----
R_sim, L_sim = [], []
for p in p_grid:
    ok = 0
    lat_acc = []
    for _ in range(N):
        legs_ok = True
        t = 0.0
        for _leg in range(Nc):
            s, nf = sim_leg_loss(p)
            t += nf * To + d + abs(rng.normal(0, jit))
            if not s:
                legs_ok = False
        if legs_ok:
            ok += 1
            lat_acc.append(t)
    R_sim.append(R0 * ok / N)
    L_sim.append(np.mean(lat_acc) if lat_acc else np.nan)
R_sim = np.array(R_sim); L_sim = np.array(L_sim)

# ---- analytical closed forms ----
R_an = R0 * (1 - p_grid**(r + 1))**Nc
with np.errstate(divide="ignore", invalid="ignore"):
    retx_mean = np.where(p_grid < 1, p_grid * (1 - p_grid**r) / (1 - p_grid), r)
retx_mean = np.nan_to_num(retx_mean, nan=r)
L_an = Nc * (retx_mean * To + d)

# ---- corruption / false-abort ----
F_sim, Rc_sim = [], []
for pc in pc_grid:
    checks_pass = (rng.random((N, 2)) > pc).all(axis=1)   # both integrity checks pass
    Rc_sim.append(R0 * checks_pass.mean())
    F_sim.append(1 - checks_pass.mean())
F_sim = np.array(F_sim); Rc_sim = np.array(Rc_sim)
F_an  = 1 - (1 - pc_grid)**2
Rc_an = R0 * (1 - pc_grid)**2

# ---- report ----
print("p      R_sim   R_analytic    L_sim   L_analytic")
for i, p in enumerate(p_grid):
    print(f"{p:4.2f}   {R_sim[i]:5.3f}    {R_an[i]:5.3f}      "
          f"{L_sim[i]:5.2f}    {L_an[i]:5.2f}")
err = np.nanmax(np.abs(R_sim - R_an))
print(f"\nMax |R_sim - R_analytic| = {err:.3f}  (should be small -> model validated)")

# ---- plots ----
fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
ax[0].plot(p_grid, R_sim, "o", label="simulation")
ax[0].plot(p_grid, R_an, "--", label=r"$R_0(1-p^{r+1})^3$")
ax[0].set_xlabel("packet-loss prob p"); ax[0].set_ylabel("throughput R")
ax[0].set_title("Throughput vs loss"); ax[0].legend(); ax[0].grid(True)

ax[1].plot(p_grid, L_sim, "o", label="simulation")
ax[1].plot(p_grid, L_an, "--", label=r"$3[\,\frac{p(1-p^r)}{1-p}T_o + d\,]$")
ax[1].set_xlabel("packet-loss prob p"); ax[1].set_ylabel("latency L")
ax[1].set_title("Latency vs loss"); ax[1].legend(); ax[1].grid(True)

ax[2].plot(pc_grid, F_sim, "o", color="C3", label="false-abort (sim)")
ax[2].plot(pc_grid, F_an, "--", color="C3", label=r"$1-(1-p_c)^2$")
ax[2].plot(pc_grid, Rc_sim, "s", color="C0", label="throughput (sim)")
ax[2].plot(pc_grid, Rc_an, "--", color="C0", label=r"$R_0(1-p_c)^2$")
ax[2].set_xlabel("corruption prob $p_c$"); ax[2].set_ylabel("probability")
ax[2].set_title("Corruption -> false-abort"); ax[2].legend(); ax[2].grid(True)

fig.tight_layout()
out = os.path.join(HERE, "qsdc_channel_sim.png")
fig.savefig(out, dpi=120)
print("Saved plot to", out)
