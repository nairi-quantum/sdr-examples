# Nairi Quantum — SDR / GNU Radio Examples

A starter set of software-defined-radio examples for the Nairi Quantum team, built
**simulation-first**: the `*_sim.py` scripts run with only **NumPy + Matplotlib** (no GNU Radio,
no hardware), so everyone can run them today. The `*_gr.py` scripts are the **GNU Radio** versions,
and the USRP examples need a **B210**.

> New to GNU Radio? Read **`NairiQuantum_GNURadio_Guide.docx`** (install + setup + flowgraph basics)
> first — it's the companion to this repo.

## Layout

| Folder | Concept | Runs with no hardware? |
|---|---|---|
| `01_tone_to_file` | Generate a complex tone, save IQ to file | ✅ (`_sim.py`) |
| `02_bpsk_loopback` | BPSK → AWGN channel → demod, measure BER vs theory | ✅ (`_sim.py`) |
| `03_spectrum_sensing` | Multi-tone + noise → PSD → detect occupied bands | ✅ (`_sim.py`) |
| `04_usrp_tx` | Transmit a tone/BPSK on a USRP B210 | ❌ needs B210 + GNU Radio + UHD |
| `05_usrp_rx` | Receive + record IQ on a USRP B210 | ❌ needs B210 + GNU Radio + UHD |
| `06_qsdc_channel` | QSDC classical-channel model (loss/ARQ/jitter/false-abort) — validates Nathalie's analytical model | ✅ (`_sim.py`) |

Each folder has its own `README.md` with the flowgraph, how to run, and expected output.

## Quick start (simulation, no hardware)

```bash
python -m pip install numpy matplotlib
python 01_tone_to_file/tone_to_file_sim.py
python 02_bpsk_loopback/bpsk_loopback_sim.py
python 03_spectrum_sensing/spectrum_sensing_sim.py
```

Each `_sim.py` prints results and saves a `*.png` plot in its folder.

## Running the GNU Radio versions

Requires GNU Radio (3.10+). See the guide. Then:

```bash
python 02_bpsk_loopback/bpsk_loopback_gr.py
```

or open the flowgraph in GNU Radio Companion (GRC) if a `.grc` is provided.

## Running the USRP examples

Requires a **USRP B210**, UHD drivers, and GNU Radio. Confirm the device first:

```bash
uhd_find_devices
uhd_usrp_probe
```

Then edit the center frequency / gain / sample rate near the top of the script and run.
**Always transmit into a cable/attenuator or a shielded setup — not over the air on arbitrary bands.**

---
Nairi Quantum · nairiquantum.org
