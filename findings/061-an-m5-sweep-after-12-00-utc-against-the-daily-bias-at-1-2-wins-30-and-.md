# Finding 61 - An M5 sweep after 12:00 UTC against the daily bias at 1:2 wins 30% and needs 36%. Negative on 15 of 15 markets and 28 of 28 years.

`sweep1200.py` (prereg `sweep1200_m5_against_bias`, sha f0a9c3c4). User's
rule from two chart pictures: from 12:00 UTC look on M5 for a sweep (bar
takes out the last confirmed swing, closes back through it); enter next
bar, SL at the sweep extreme, TP 2R; daily bias bearish → buys only,
bullish → sells only; nothing by 16:00 → no trade. M5 pulled from Deriv
(`data/bars/forex_m5`, 1999+ forex, 2011+ gold), 77,124 trades.

Rule −0.098 R (t −19.9, both halves negative, 30.4% win); with-bias
control −0.100; no bias −0.102; window 08-12 −0.092; 04-08 −0.132. Every
market negative (USDCAD best at −0.050, EURCHF worst at −0.185); 0 of 28
years positive. Target 29%, stop 69%, median R 12.5 spreads. Prediction
held. Neither the bias nor the window is in the result. **Rejected; nothing
built.**

---
[All findings](../README.md)
