#!/usr/bin/env python3
"""03 - Spectrum sensing (GNU Radio version, GUI).

Flowgraph:
  Signal Sources (a few tones) + Noise Source --> Add --> Throttle --> QT GUI Freq Sink

Requires GNU Radio 3.10+ with the QT GUI. Run:  python spectrum_sensing_gr.py
(Opens a live spectrum window.) For a headless / algorithmic version that also
DETECTS the occupied bands, use spectrum_sensing_sim.py.
"""
import sys
import signal
from PyQt5 import Qt
from gnuradio import gr, blocks, analog, qtgui
from gnuradio.filter import firdes  # noqa: F401 (commonly needed)

class spectrum_sensing(gr.top_block, Qt.QWidget):
    def __init__(self, samp_rate=2_000_000):
        gr.top_block.__init__(self, "Spectrum sensing")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Nairi Quantum - Spectrum Sensing")
        layout = Qt.QVBoxLayout(self)

        tones = [(-600_000, 0.7), (150_000, 1.0), (700_000, 0.4)]
        adder = blocks.add_vcc(1)
        srcs = []
        for i, (f, a) in enumerate(tones):
            s = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, f, a, 0)
            srcs.append(s)
            self.connect(s, (adder, i))
        noise = analog.noise_source_c(analog.GR_GAUSSIAN, 0.1, 0)
        self.connect(noise, (adder, len(tones)))

        throttle = blocks.throttle(gr.sizeof_gr_complex, samp_rate, True)
        self.freq_sink = qtgui.freq_sink_c(4096, firdes.WIN_HANN if hasattr(firdes, "WIN_HANN") else 0,
                                           0, samp_rate, "PSD", 1)
        self.connect(adder, throttle, self.freq_sink)
        layout.addWidget(self.freq_sink.qwidget())


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    tb = spectrum_sensing()
    tb.start()
    tb.show()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec_()
    tb.stop(); tb.wait()
