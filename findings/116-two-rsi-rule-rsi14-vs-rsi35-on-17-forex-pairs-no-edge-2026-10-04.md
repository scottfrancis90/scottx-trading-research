# Finding 116 - Two-RSI rule (RSI14 vs RSI35) on 17 forex pairs: no edge (2026-10-04)

Source idea: a screenshot of an account showing daily RSI14 + RSI35. The account
itself could not be used to learn the rule: all 15 open positions were created
on 2026-08-31 05:54-06:10 server time (time_update matches the shown open time
to the second, tickets ordered by that creation, not by the shown June-August
dates). Rule defined from first principles instead, no tuning. ml/rsi2.py.

A daily cross-and-reverse: 17 pairs, mean edge over matched random +0.018 ATR,
t 0.58, positive on 7/17. Only EURUSD/USDCHF positive, and entirely from
1971-1992 (+1.0 ATR); 1993-2026 both negative. Pooled 2017-2026 -0.069 ATR, t -3.34.
B daily direction + 4H cross entry: edge -0.006 ATR, t -0.97; pooled negative
in every era (t -4.2, -2.7, -5.9) after 2-pip costs.
GBPCHF not tested: history download from a second terminal hung (weekend).
Verdict: dead in both forms.

---
[All findings](../README.md)
