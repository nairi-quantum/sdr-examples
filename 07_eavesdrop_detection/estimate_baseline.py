# -*- coding: utf-8 -*-
"""Estimate the excess noise xi from GNU Radio File Sink captures (Lilit's estimator).

Run this AFTER the GNU Radio flowgraph (see README) has written Alice's and Bob's
complex64 streams to disk:

    alice_s.dat   (Alice's transmitted symbols s)
    bob_y.dat     (Bob's received symbols y)

Usage:
    python estimate_baseline.py                 # reads alice_s.dat / bob_y.dat here
    python estimate_baseline.py alice.dat bob.dat

Decision rule:  alarm if  xi_hat > xi_th,  with  xi_th = Qinv(P_fa) / sqrt(M).
In this software baseline Bob subtracts Alice's known s; on a real link the excess
noise is estimated from a disclosed subset of symbols and a calibrated noise floor.
"""
import sys
import numpy as np
from math import erfc
from pathlib import Path

P_FA = 0.01    # false-alarm probability
N0   = 1.0     # calibrated baseline (shot-noise) variance per quadrature

def Q(x):
    return 0.5 * erfc(x / np.sqrt(2.0))

def Qinv(p):
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if Q(mid) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

def main(argv):
    here = Path(__file__).resolve().parent
    s_path = Path(argv[1]) if len(argv) > 1 else here / "alice_s.dat"
    y_path = Path(argv[2]) if len(argv) > 2 else here / "bob_y.dat"

    s = np.fromfile(s_path, dtype=np.complex64)
    y = np.fromfile(y_path, dtype=np.complex64)
    if len(s) == 0 or len(y) == 0:
        raise SystemExit(f"Empty capture: {s_path} ({len(s)}), {y_path} ({len(y)})")
    M = min(len(s), len(y))
    s, y = s[:M], y[:M]

    r = y - s
    xi_hat = np.mean(np.abs(r) ** 2) / 2.0 - N0
    xi_th = Qinv(P_FA) / np.sqrt(M)
    decision = "ALARM" if xi_hat > xi_th else "No alarm"

    print(f"Alice samples: {len(s)}")
    print(f"Bob samples:   {len(y)}")
    print(f"I-noise variance: {np.var(r.real):.6f}")
    print(f"Q-noise variance: {np.var(r.imag):.6f}")
    print(f"Estimated xi:  {xi_hat:.6f}")
    print(f"Threshold:     {xi_th:.6f}   (P_fa={P_FA}, M={M})")
    print(f"Decision:      {decision}")

if __name__ == "__main__":
    main(sys.argv)
