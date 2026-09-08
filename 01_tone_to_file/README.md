# 01 — Tone to file

The "hello world" of SDR: generate a complex tone and save it as raw IQ.

```
Signal Source (cosine) --> Throttle --> File Sink (complex float32)
```

**Concepts:** complex (I/Q) samples, sample rate vs. tone frequency, the raw
interleaved-`float32` file format GNU Radio uses (`np.complex64`).

## Run (no hardware)
```bash
python tone_to_file_sim.py
```
Writes `tone.iq` and `tone_to_file_sim.png`. The spectrum shows a single peak at
+100 kHz (a complex tone is one-sided — this is the key difference from a real cosine).

## Run (GNU Radio)
```bash
python tone_to_file_gr.py     # writes tone_gr.iq
```

## Read the IQ back anywhere
```python
import numpy as np
iq = np.fromfile("tone.iq", np.complex64)
```
