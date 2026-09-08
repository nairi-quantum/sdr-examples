# 06 — QSDC classical coordination channel

The bridge between the SDR examples and **Nathalie's paper**. Instead of a plain AWGN
channel (example 02), this models the *classical* coordination channel a DL04-style
QSDC session relies on — packet loss, ARQ retransmission, delay/jitter, and
corruption-driven false aborts — and validates the paper's closed-form model against
Monte-Carlo simulation.

```
QSDC session = 3 legs (Bob->Alice->Bob)
  per leg: control packet lost w.p. p, retransmit up to r times (ARQ)
```

## Analytical model (overlaid as dashed curves)
- **Throughput:**  `R(p) = R0 · (1 − p^(r+1))^3`
- **Latency:**  `L(p) = 3 · [ p(1−p^r)/(1−p) · To + d ]`
- **Corruption / false-abort (two checks):**  `F(pc) = 1 − (1−pc)^2`,  surviving `R(pc) = R0 · (1−pc)^2`

## Run (no hardware)
```bash
python qsdc_channel_sim.py
```
Prints a sim-vs-analytic table and saves `qsdc_channel_sim.png` (three panels:
throughput, latency, corruption→false-abort).

**Expected:** the throughput simulation lands on the analytical curve (max error ~0.003).
The latency simulation sits **slightly above** the closed form — that gap is the
**jitter** term (mean ≈ `3 · jit · √(2/π)`), which the analytical `L(p)` deliberately
omits. Seeing that offset is the point: it shows where the model is exact and where a
correction term applies.

## Why this matters
This is the software analogue of Nathalie's QSDC-over-imperfect-classical-channel work,
and a natural place to (a) validate the analytical formulas, (b) plug in a real SDR
channel (from examples 04/05) in place of the statistical loss model, and (c) later
drive it with measured impairments from the testbed.
