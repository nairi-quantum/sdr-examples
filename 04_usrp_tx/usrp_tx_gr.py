#!/usr/bin/env python3
"""04 - USRP transmit (GNU Radio + UHD).  *** REQUIRES A USRP B210 ***

Flowgraph:  Signal Source (tone) --> Multiply const (gain) --> UHD USRP Sink

Safety: transmit into a CABLE + ATTENUATOR or a shielded enclosure. Do not radiate
on arbitrary frequencies. Pick a legal/lab frequency and a low gain to start.

Setup check first:
    uhd_find_devices
    uhd_usrp_probe
Run:
    python usrp_tx_gr.py
"""
import time
from gnuradio import gr, blocks, analog, uhd

# ---- EDIT THESE ----
CENTER_FREQ = 915e6      # Hz  (use a legal/lab band; 915 MHz ISM as an example)
SAMP_RATE   = 1e6        # Hz
TONE_OFFSET = 100e3      # Hz, tone offset from center
TX_GAIN_DB  = 30         # start LOW, increase carefully
AMPLITUDE   = 0.3
# --------------------

class usrp_tx(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "USRP TX tone")

        src = analog.sig_source_c(SAMP_RATE, analog.GR_COS_WAVE,
                                  TONE_OFFSET, AMPLITUDE, 0)
        self.sink = uhd.usrp_sink(
            ",".join(("", "")),
            uhd.stream_args(cpu_format="fc32", channels=[0]),
        )
        self.sink.set_samp_rate(SAMP_RATE)
        self.sink.set_center_freq(CENTER_FREQ, 0)
        self.sink.set_gain(TX_GAIN_DB, 0)
        self.sink.set_antenna("TX/RX", 0)

        self.connect(src, self.sink)


if __name__ == "__main__":
    tb = usrp_tx()
    print(f"Transmitting a {TONE_OFFSET/1e3:.0f} kHz tone at "
          f"{CENTER_FREQ/1e6:.3f} MHz, gain {TX_GAIN_DB} dB. Ctrl-C to stop.")
    tb.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    tb.stop(); tb.wait()
    print("Stopped.")
