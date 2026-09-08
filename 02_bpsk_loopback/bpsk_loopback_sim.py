#!/usr/bin/env python3
"""02 - BPSK loopback over an AWGN channel (pure NumPy, runnable now).

Transmit random bits with BPSK, add complex AWGN for a range of Eb/N0, demodulate,
and compare the measured bit-error rate (BER) to the theoretical curve.
This is the software 'loopback' equivalent of TX -> channel -> RX.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import numpy as np
from numpy import sqrt
from math import erfc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(12345)

N = 200_000                       # bits
ebn0_db = np.arange(0, 11)        # 0..10 dB
ber = np.zeros(len(ebn0_db))

bits = rng.integers(0, 2, N)
symbols = 2 * bits - 1            # BPSK: 0->-1, 1->+1  (energy per bit = 1)

for i, snr_db in enumerate(ebn0_db):
    ebn0 = 10 ** (snr_db / 10)
    # complex AWGN; noise variance per complex sample = 1/(2*Eb/N0) per component
    sigma = sqrt(1 / (2 * ebn0))
    noise = sigma * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    rx = symbols + noise
    bits_hat = (rx.real > 0).astype(int)
    ber[i] = np.mean(bits_hat != bits)

# Theoretical BPSK BER: Q(sqrt(2*Eb/N0)) = 0.5*erfc(sqrt(Eb/N0))
theory = np.array([0.5 * erfc(sqrt(10 ** (s / 10))) for s in ebn0_db])

print(" Eb/N0(dB)   measured BER   theory BER")
for s, m, th in zip(ebn0_db, ber, theory):
    print(f"   {s:5d}     {m:10.2e}   {th:10.2e}")

plt.figure(figsize=(7, 5))
plt.semilogy(ebn0_db, np.maximum(ber, 1e-6), "o-", label="measured")
plt.semilogy(ebn0_db, np.maximum(theory, 1e-12), "k--", label="theory  0.5*erfc(sqrt(Eb/N0))")
plt.xlabel("Eb/N0 (dB)"); plt.ylabel("BER"); plt.grid(True, which="both")
plt.title("BPSK over AWGN — loopback simulation"); plt.legend()
out = os.path.join(HERE, "bpsk_loopback_sim.png")
plt.tight_layout(); plt.savefig(out, dpi=120)
print("Saved plot to", out)
