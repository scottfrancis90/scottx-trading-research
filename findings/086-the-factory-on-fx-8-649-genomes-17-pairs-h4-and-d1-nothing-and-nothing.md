# Finding 86 - the factory on FX: 8,649 genomes, 17 pairs, H4 and D1. Nothing, and nothing fake either.

*2026-09-27. Pre-registered in `factory/runs/PREREG_fx.md` before the run.
79 minutes, ledger 7,795 -> 8,649.*

### The verdict

**NO SURVIVORS**, and unlike every gold run the failure is clean: the best
genome the search could find was **NEGATIVE on TRAIN**, mean -0.0104 over 2,137
pooled trades. Fitness never crossed zero in 20 generations. There was no
artifact to unwind, no spike to explain -- the search looked and found nothing.

Top candidate, `D1 | weekly_range(2) | break_level(best_room) | other_side |
r_multiple(1.0) | hold 24h`:

```
  TRAIN      n=2137  mean -0.0104
  [FAIL] both halves positive      -0.0153 / -0.0165
  [FAIL] Bonferroni                t -6.92, need 5.02   (significant the WRONG way)
  [FAIL] inverted control          mirror -0.0101, edge -0.0058
  [PASS] shuffled direction flat   -0.0151
  [FAIL] pairs positive            3 of 16
  [FAIL] classify                  COLLAPSE (StraddleX, 3/4 slots)
```

**Both directions lose** (-0.0104 and -0.0101). The cost signature, for the
fourth time today. 12 of 12 candidates were `weekly_range | break_level |
other_side | r_multiple`; 7 more were dropped as duplicate trade books.

### All four pre-registered predictions held

| predicted | outcome |
|---|---|
| no survivors | none |
| survivors would be breakout/straddle shapes | `break_level` x12, 99% known-skeleton share |
| chapter entries would not dominate | zero chapters in the top 12 |
| the pairs gate would bite | 3 of 16 |

### What the user contributed, and it is all now in the machine

* **The daily timeframe.** *"daily time frame is ment for anything that can give
  money... but we aviod it because it take time and boring"*. D1 was not in the
  factory's vocabulary at all. Measured: cost of a 1-ATR stop is 7.4% of R on
  M30, 3.6% on H4, **1.9% on D1** -- daily is 4x cheaper per unit of risk. FX
  was restricted to H4/D1 on that basis and 9 of the 12 candidates chose D1.
* **The signal cooldown.** *"it help to remove nonsense trade"*. Measured on
  M15: cool 0/24/72h gave +0.2305/+0.2510/+0.2760 on fewer and fewer trades.
  It is now its own gene, separate from the hold.
* **Timeout in bars.** *"you cant use same number you use for htf for LTF"*.
  Correct -- 100 bars is 8 hours on M5 and 16 days on H4 while the GA mutated
  it as one quantity. Now in hours.
* **Opposite pairs.** *"jpy fmailer sell like etc"*. This broke the gate I had
  built an hour earlier. Measured: mean |r| 0.37 across the 17 pairs, AUDJPY
  and NZDJPY at +0.87, and the EFFECTIVE number of independent bets is **5.3,
  not 17**. Six JPY crosses all turning positive is 2.2 confirmations, not 6.
  The gate now counts independent information via the eigenvalue entropy of the
  correlation sub-matrix, not rows. (Single-linkage clustering was tried first
  and rejected -- at |r|>0.60 it chained 14 of 17 pairs into one group.)

Every one of those was a real correction to the machine, and the machine with
all of them in it still found nothing.

### Data defect fixed before the run

`forex_h1` files are concatenations: daily history carrying hourly timestamps
(~260 bars a year where H1 shows ~6,000), then real H1 from 1999. EURUSD,
USDCHF and USDJPY began in **1971**, before the euro existed. Only 0-4% of
bars, but at the START of the series, which is the TRAIN split. Every pair is
now truncated to its first year holding >= 3,000 bars.

**Status: no tradable rule on gold or on 17 FX pairs. Every holdout still
clean. Nothing built, no money risked.**

---

---
[All findings](../README.md)
