#!/usr/bin/env python3
"""05 - USRP receive + record (GNU Radio + UHD).  *** REQUIRES A USRP B210 ***

Flowgraph:  UHD USRP Source --> Throttle(off when live) --> File Sink (complex)

Captures a few seconds of IQ to 'capture.iq' (complex float32). Analyze it later with
numpy (np.fromfile('capture.iq', np.complex64)) or feed it to 03_spectrum_sensing.

Setup check first:
    uhd_find_devices ; uhd_usrp_probe
Run:
    python usrp_rx_gr.py
"""
import os
import time
from gnuradio import gr, blocks, uhd

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- EDIT THESE ----
CENTER_FREQ = 915e6      # Hz
SAMP_RATE   = 2e6        # Hz
RX_GAIN_DB  = 40
CAPTURE_SEC = 3
# --------------------

class usrp_rx(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "USRP RX capture")
        out_file = os.path.join(HERE, "capture.iq")

        self.src = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(cpu_format="fc32", channels=[0]),
        )
        self.src.set_samp_rate(SAMP_RATE)
        self.src.set_center_freq(CENTER_FREQ, 0)
        self.src.set_gain(RX_GAIN_DB, 0)
        self.src.set_antenna("RX2", 0)

        sink = blocks.file_sink(gr.sizeof_gr_complex, out_file, False)
        sink.set_unbuffered(False)
        self.connect(self.src, sink)


if __name__ == "__main__":
    tb = usrp_rx()
    print(f"Capturing {CAPTURE_SEC}s at {CENTER_FREQ/1e6:.3f} MHz, "
          f"{SAMP_RATE/1e6:.1f} Msps, gain {RX_GAIN_DB} dB ...")
    tb.start(); time.sleep(CAPTURE_SEC); tb.stop(); tb.wait()
    print("Saved IQ to", os.path.join(HERE, "capture.iq"))
