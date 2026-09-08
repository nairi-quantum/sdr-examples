# 05 — USRP receive + record  (requires a USRP B210)

Capture live IQ from a USRP B210 to a file for offline analysis.

```
UHD USRP Source --> File Sink (complex float32)  ->  capture.iq
```

**Requires:** USRP B210, UHD drivers, GNU Radio 3.10+.

## Before you run
```bash
uhd_find_devices ; uhd_usrp_probe
```
Edit `CENTER_FREQ`, `SAMP_RATE`, `RX_GAIN_DB`, `CAPTURE_SEC` at the top, then:
```bash
python usrp_rx_gr.py      # writes capture.iq
```

## Analyze the capture (no hardware needed afterwards)
```python
import numpy as np
iq = np.fromfile("capture.iq", np.complex64)
```
Feed `iq` into the PSD code from `03_spectrum_sensing` to see what's on the air.
Pair with `04_usrp_tx` (a second device transmitting a tone) for a full TX→RX loop.
