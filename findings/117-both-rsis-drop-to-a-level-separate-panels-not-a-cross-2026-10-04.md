# Finding 117 - "Both RSIs drop to a level" (separate panels, not a cross) (2026-10-04)

ml/rsi_levels.py. 17 pairs, 1993+, 6 level pairs x 3 holds x 2 sides = 36 cells,
edge over all-days baseline, t across pairs. 4 cells t>+2, 2 cells t<-2 (about 2
expected by chance each way, cells are correlated). The positives share one
theme, MEAN REVERSION: buy when RSI14<=35 & RSI35<=45 (+0.058/+0.131 ATR at 5d/20d,
t 2.1/2.4, 10-12 of 17 pairs) and sell when both >=50 held 20d (+0.094, t 3.1,
14/17). Buying when both dip to 50 (the pullback reading) is negative.
Not confirmed: found by search over the grid. Needs an untouched test.

---
[All findings](../README.md)
