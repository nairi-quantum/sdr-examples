#!/usr/bin/env python3
"""01 - Tone to file (GNU Radio version).

Flowgraph:  Signal Source (cosine) --> Throttle --> File Sink (complex)

Requires GNU Radio 3.10+. Run:  python tone_to_file_gr.py
Produces 'tone_gr.iq' (interleaved complex float32), readable by a File Source
or by numpy:  np.fromfile('tone_gr.iq', np.complex64)
"""
import os
import time
from gnuradio import gr, blocks, analog

HERE = os.path.dirname(os.path.abspath(__file__))

class tone_to_file(gr.top_block):
    def __init__(self, samp_rate=1_000_000, tone_freq=100_000, amplitude=0.5):
        gr.top_block.__init__(self, "Tone to File")
        out_file = os.path.join(HERE, "tone_gr.iq")

        src = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE,
                                  tone_freq, amplitude, 0)
        throttle = blocks.throttle(gr.sizeof_gr_complex, samp_rate, True)
        sink = blocks.file_sink(gr.sizeof_gr_complex, out_file, False)
        sink.set_unbuffered(False)

        self.connect(src, throttle, sink)


if __name__ == "__main__":
    tb = tone_to_file()
    tb.start()
    time.sleep(1)          # capture ~1 second of samples
    tb.stop()
    tb.wait()
    print("Done. Wrote", os.path.join(HERE, "tone_gr.iq"))
