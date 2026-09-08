# 04 — USRP transmit  (requires a USRP B210)

Transmit a tone from a USRP B210.

```
Signal Source (tone) --> gain --> UHD USRP Sink  --> antenna/cable
```

**Requires:** USRP B210, UHD drivers, GNU Radio 3.10+.

## Before you run
```bash
uhd_find_devices     # confirm the B210 is seen
uhd_usrp_probe       # check firmware/FPGA + capabilities
```
Edit `CENTER_FREQ`, `SAMP_RATE`, `TX_GAIN_DB` at the top of `usrp_tx_gr.py`.

```bash
python usrp_tx_gr.py     # Ctrl-C to stop
```

## Safety
- Transmit into a **cable + attenuator** or a shielded enclosure — do **not** radiate on
  arbitrary bands.
- Start at **low gain** and increase carefully.
- Pair with `05_usrp_rx` on a second device (or the same B210's RX) to see the tone.
