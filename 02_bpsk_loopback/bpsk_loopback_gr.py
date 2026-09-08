#!/usr/bin/env python3
"""02 - BPSK loopback over AWGN (GNU Radio version).

Flowgraph:
  Random Source (bits) --> Chunks-to-Symbols (BPSK) --> Throttle
      --> Channel Model (AWGN) --> Complex-to-Real --> Binary Slicer --> File Sink

Requires GNU Radio 3.10+.  This mirrors bpsk_loopback_sim.py but through GNU Radio
blocks. For a full BER curve, the NumPy version is easier; this shows the block wiring.
"""
import os
import time
from gnuradio import gr, blocks, digital, channels

HERE = os.path.dirname(os.path.abspath(__file__))

class bpsk_loopback(gr.top_block):
    def __init__(self, samp_rate=1_000_000, noise_volt=0.3):
        gr.top_block.__init__(self, "BPSK loopback (AWGN)")

        # random bytes -> unpack to bits
        src = blocks.vector_source_b(
            list((os.urandom(20000))), True)           # repeating random bytes
        unpack = blocks.unpack_k_bits_bb(8)            # bytes -> bits (0/1)

        # BPSK constellation: bit 0 -> -1, bit 1 -> +1
        const = digital.constellation_bpsk().base()
        mod = digital.chunks_to_symbols_bc(const.points(), 1)

        throttle = blocks.throttle(gr.sizeof_gr_complex, samp_rate, True)
        chan = channels.channel_model(noise_voltage=noise_volt,
                                      frequency_offset=0.0,
                                      epsilon=1.0, taps=[1.0], noise_seed=0)

        # demod: take real part, slice at 0
        to_real = blocks.complex_to_real(1)
        slicer = digital.binary_slicer_fb()
        sink = blocks.file_sink(gr.sizeof_char,
                                os.path.join(HERE, "rx_bits.u8"), False)

        self.connect(src, unpack, mod, throttle, chan, to_real, slicer, sink)


if __name__ == "__main__":
    tb = bpsk_loopback()
    tb.start(); time.sleep(1); tb.stop(); tb.wait()
    print("Done. Received bits written to", os.path.join(HERE, "rx_bits.u8"))
