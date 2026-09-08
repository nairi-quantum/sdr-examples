# 03 — Spectrum sensing

Look at a chunk of spectrum, estimate the power across frequency, and decide which
channels are occupied — the basis of spectrum monitoring and cognitive radio.

```
tones + noise --> PSD (Welch) --> threshold --> occupied-band list
```

**Concepts:** PSD / Welch averaging, FFT windowing (Hann), noise floor, an
energy-detection threshold, grouping contiguous bins into "bands."

## Run (no hardware)
```bash
python spectrum_sensing_sim.py
```
Prints the detected occupied bands (should find the 3 planted tones near −600, +150,
+700 kHz) and saves `spectrum_sensing_sim.png` with the occupied regions shaded.

## Run (GNU Radio, live GUI)
```bash
python spectrum_sensing_gr.py
```
Opens a live QT frequency-sink window. Replace the tone sources with a **USRP source**
(see `04_usrp_rx`) to sense the real RF environment.
