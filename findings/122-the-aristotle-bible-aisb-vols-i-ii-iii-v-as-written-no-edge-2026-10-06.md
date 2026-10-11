# Finding 122 - The Aristotle Bible (AISB), Vols I/II/III/V as written: no edge (2026-10-06)

ml/aristotle.py, rules from the user's Google Doc + pasted Vol I/II/III/V code.
XAUUSD M15 2004-2026 (Dukascopy + MT5). Asia 20-00 NY range (>= $2.50), PDH/PDL,
London H/L for NY; levels die on a 15M close through; sweep = wick through + close
back inside, in London 02-05 or NY 08:30-11 kill zone; stop beyond wick + $0.25;
target opposite Asia, else PDH/PDL, must be >= 2R; flat 17:00 NY; $0.35 cost.
Three entries from the Bible: A sweep close (Vol III), B BOS candle (Vol I),
C retrace + rejection (Vol V). Bias as written: last closed 4H candle + premium/
discount vs previous-day midpoint. Matched random control, 30 per trade.
WITH bias: A -0.454 R (edge vs random -0.184, t -2.9), B -0.242 (n 228),
C -0.235 (edge -0.057). The bias makes it WORSE than no bias in all three.
NO bias: A -0.319, B -0.067 (edge +0.059 t 0.86, DEV +0.067 / VAL +0.050),
C -0.173 (edge +0.038 t 0.86). Gross of cost: B +0.082 R, others ~0.
Median stop only $1.4-2.8, so cost is 13-24% of R. Win rate 21-30% against
average targets of 4.5-8.9R. Verdict: no version beats random entry with the
same stop and target; all lose after costs. Vol VII (Asia directional) untested.

---
[All findings](../README.md)
