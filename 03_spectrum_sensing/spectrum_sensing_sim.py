#!/usr/bin/env python3
"""03 - Spectrum sensing (pure NumPy, runnable now).

Build a wideband signal with a few tones (occupied channels) plus noise, estimate
the power spectral density (Welch), and flag bands whose power exceeds a threshold.
This is the basis of cognitive-radio / spectrum-monitoring work.
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
rng = np.random.default_rng(7)

samp_rate = 2_000_000        # 2 Msps -> observe -1..+1 MHz
n = 262144
t = np.arange(n) / samp_rate

# Occupied "channels" (offset freq in Hz, amplitude)
tones = [(-600_000, 0.7), (150_000, 1.0), (700_000, 0.4)]
x = np.zeros(n, dtype=np.complex128)
for f, a in tones:
    x += a * np.exp(2j * np.pi * f * t)
x += 0.1 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))  # noise floor

# --- Welch PSD ---
nfft = 4096
win = np.hanning(nfft)
segs = n // nfft
psd = np.zeros(nfft)
for k in range(segs):
    seg = x[k * nfft:(k + 1) * nfft] * win
    psd += np.abs(np.fft.fftshift(np.fft.fft(seg))) ** 2
psd /= segs
psd_db = 10 * np.log10(psd / psd.max() + 1e-12)
freqs = np.fft.fftshift(np.fft.fftfreq(nfft, 1 / samp_rate)) / 1e3  # kHz

# --- Detect occupied bands (threshold above noise floor) ---
noise_floor = np.median(psd_db)
threshold = noise_floor + 10.0     # dB
occupied = psd_db > threshold
print(f"Noise floor ~ {noise_floor:.1f} dB, threshold = {threshold:.1f} dB")
print("Detected occupied frequencies (kHz):")
# group contiguous detections
idx = np.where(occupied)[0]
if len(idx):
    groups = np.split(idx, np.where(np.diff(idx) > 3)[0] + 1)
    for g in groups:
        f0, f1 = freqs[g[0]], freqs[g[-1]]
        peak = freqs[g[np.argmax(psd_db[g])]]
        print(f"   band {f0:8.0f} .. {f1:8.0f} kHz   (peak ~ {peak:.0f} kHz)")

plt.figure(figsize=(9, 5))
plt.plot(freqs, psd_db, label="PSD")
plt.axhline(threshold, color="r", ls="--", label="threshold")
plt.fill_between(freqs, -120, psd_db, where=occupied, color="orange", alpha=0.3,
                 label="detected")
plt.xlabel("frequency (kHz)"); plt.ylabel("power (dB, normalized)")
plt.title("Spectrum sensing — 3 occupied channels detected"); plt.legend()
plt.grid(True)
out = os.path.join(HERE, "spectrum_sensing_sim.png")
plt.tight_layout(); plt.savefig(out, dpi=120)
print("Saved plot to", out)
