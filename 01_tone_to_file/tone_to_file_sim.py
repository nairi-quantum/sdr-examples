#!/usr/bin/env python3
"""01 - Tone to file (pure NumPy, no GNU Radio, no hardware).

Generates a complex exponential (a single tone) at a chosen frequency and sample
rate, writes it to a raw IQ file (interleaved complex float32 -- the same format
GNU Radio's File Sink uses), and plots the first cycles + the spectrum.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

samp_rate = 1_000_000       # 1 Msps
tone_freq = 100_000         # 100 kHz tone
n_samples = 100_000
amplitude = 0.5

t = np.arange(n_samples) / samp_rate
iq = amplitude * np.exp(2j * np.pi * tone_freq * t)   # complex tone
iq = iq.astype(np.complex64)

# Save as interleaved float32 (GNU Radio "complex" file format)
out_bin = os.path.join(HERE, "tone.iq")
iq.view(np.float32).tofile(out_bin)
print(f"Wrote {iq.size} complex samples to {out_bin} "
      f"({os.path.getsize(out_bin)} bytes, complex float32).")

# --- Plots ---
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
show = 200
ax[0].plot(t[:show] * 1e6, iq[:show].real, label="I")
ax[0].plot(t[:show] * 1e6, iq[:show].imag, label="Q")
ax[0].set_xlabel("time (us)"); ax[0].set_ylabel("amplitude")
ax[0].set_title("Complex tone (time domain)"); ax[0].legend(); ax[0].grid(True)

spec = np.fft.fftshift(np.fft.fft(iq[:8192]))
freqs = np.fft.fftshift(np.fft.fftfreq(8192, 1 / samp_rate)) / 1e3
ax[1].plot(freqs, 20 * np.log10(np.abs(spec) + 1e-9))
ax[1].set_xlabel("frequency (kHz)"); ax[1].set_ylabel("magnitude (dB)")
ax[1].set_title("Spectrum (peak at +100 kHz)"); ax[1].grid(True)

fig.tight_layout()
out_png = os.path.join(HERE, "tone_to_file_sim.png")
fig.savefig(out_png, dpi=120)
print(f"Saved plot to {out_png}")
