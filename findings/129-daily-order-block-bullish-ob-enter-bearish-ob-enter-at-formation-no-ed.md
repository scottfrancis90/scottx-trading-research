# Finding 129 - Daily order block, "bullish OB enter, bearish OB enter" (at formation): no edge (2026-10-07)

ml/ob_daily.py. OB on its own (no FVG), two standard definitions; enter next open
after the confirming candle; stop beyond OB + $0.25 (median $34-37); 1R/2R; 20d cap.
BOS OB (last opposite candle before a close beyond a fractal swing), 562 OBs:
  1R edge vs random -0.082 (t -1.7; DEV -0.079, VAL -0.085); 2R -0.061.
Displacement OB (last opposite candle before a body >= 1 ATR candle), 637 OBs:
  1R +0.013 (DEV +0.049, VAL -0.024); 2R +0.025 (DEV +0.071, VAL -0.022).
Profitable buys are gold drift (random buys earn the same); sells lose.
With Findings 128/127: entering when an OB/FVG forms never beats random; only the
later RETEST + rejection showed a small edge.

---
[All findings](../README.md)
