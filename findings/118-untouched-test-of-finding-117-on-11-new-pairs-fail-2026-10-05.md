# Finding 118 - Untouched test of Finding 117 on 11 new pairs: FAIL (2026-10-05)

ml/rsi_untouched.py, rule frozen 2026-10-04 before data pulled. 11 major crosses
never used in Finding 117 (AUDCAD AUDCHF AUDNZD CADCHF EURNZD GBPCAD GBPCHF GBPNZD
NZDCAD NZDCHF NZDUSD), Deriv daily, 2017-02 to 2026-10 (3000 bars each).
PRIMARY BUY RSI14<=35 & RSI35<=45, hold 20d: edge +0.006 ATR, t +0.08, 8/11 -> FAIL.
SECONDARY SELL both >=50, hold 20d: edge +0.051 ATR, t +0.70, 6/11 -> FAIL.
The Finding 117 cells were search luck. Two-RSI idea closed in all three forms
(cross, cross + 4H entry, both-at-a-level).

---
[All findings](../README.md)
