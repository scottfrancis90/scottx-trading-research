# Finding 143 - FX: the first order block of the day / from London does not set the day's direction (2026-10-09)

ml/fx_first_ob.py (trades ml/fx_first_ob_trades.csv). Deriv H1, 28 pairs, 2017-2026,
UTC -> New York with DST. OB = indicator definition (BOS, swing 2). Trade the OB's
direction from the next open to the 17:00 NY close (and a variant with a stop at the OB).
First OB from LONDON (BOS 02:00-05:00 NY): 30,738 days, same direction 50.2%, -0.013 R
(t -1.3), halves -0.008 / -0.019, 14 of 28 pairs > 0 -> a coin flip.
First OB of the DAY (after the 18:00 NY open): 69,860 days, 48.7%, -0.053 R (t -7.0),
4 of 28 pairs > 0 -> slightly WORSE than a coin (the early break tends to reverse).
London bullish OB -> buy 48.5% / bearish OB -> sell 52.0% (sample-period USD lean).

---
[All findings](../README.md)
