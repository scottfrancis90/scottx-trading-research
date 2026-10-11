# Finding 121 - Break -> sweep -> sweep -> entry (H1, user's sequence): no edge (2026-10-06)

ml/break2sweep.py. User chose the definition from a diagram: high line broken up,
then two low-line sweeps on separate candles, buy next H1 open (mirror for sells).
Reset on an opposite break or 48 bars. Stop below the lower sweep wick +10%.
313 buys / 212 sells 2004-2026 (23 a year). Matched random control, 20 per trade.
Best cell: buys, 1R target, DEV +0.138 R over random (t 1.79) -> VAL +0.038 (t 0.43).
Every other cell (2R, trail 1.5R, sells) within noise of random in both halves.
Verdict: the sequence does not beat a random entry with the same stop and exit.

---
[All findings](../README.md)
