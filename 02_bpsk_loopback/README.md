# 02 — BPSK loopback over AWGN

The core comms example: transmit bits, pass through a noisy channel, recover them,
and check the bit-error rate against theory.

```
bits --> BPSK map (0->-1, 1->+1) --> AWGN channel --> slice at 0 --> bits_hat
```

**Concepts:** BPSK, Eb/N0, AWGN, hard-decision demod, BER vs. the theoretical
`0.5·erfc(√(Eb/N0))` curve. This is the "loopback" (no-hardware) version of a
real TX → channel → RX chain.

## Run (no hardware)
```bash
python bpsk_loopback_sim.py
```
Prints a measured-vs-theory BER table and saves `bpsk_loopback_sim.png`. The
measured points should sit right on the theory curve — if they don't, the noise
scaling is wrong (a classic SDR debugging lesson).

## Run (GNU Radio)
```bash
python bpsk_loopback_gr.py
```
Shows the same idea wired from GNU Radio blocks (Random source → chunks-to-symbols
→ channel model → slicer → file sink).

## Next step
Swap the AWGN channel for the QSDC classical-channel impairment model
(loss/delay/jitter) to connect this to Nathalie's work.
