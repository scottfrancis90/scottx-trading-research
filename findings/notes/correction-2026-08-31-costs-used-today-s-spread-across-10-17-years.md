# CORRECTION - 2026-08-31: costs used TODAY's spread across 10-17 years

Every cost figure in this study divided a CONSTANT present-day spread by the
stop distance. The bar data carries a per-bar `spread` field that was never
used. Gold's spread was 10-20x more expensive in the early years:

| year | spread pts | price | spread / range |
|---:|---:|---:|---:|
| 2011 | 50 | 1,545 | 0.170 |
| 2014 | 37 | 1,276 | 0.226 |
| 2018 | 16 | 1,263 | 0.119 |
| 2019-20 | **0** | 1,406-1,774 | 0.000 |
| 2023 | 1 | 1,945 | 0.004 |
| 2026 | 15 | 4,571 | 0.012 |

So the flat 0.18 UNDERSTATED cost in the 2011-2018 holdout and OVERSTATED it
in the 2018-2026 development block.

### Finding 20 re-run with per-bar spread

| | flat 0.18 (as reported) | true per-bar |
|---|---:|---:|
| holdout cost | 0.0227 | **0.0388** |
| **holdout net** | **+0.0661** | **+0.0500** |
| dev cost | 0.0151 | **0.0044** |
| **dev net** | **+0.0865** | **+0.0972** |

**Finding 20 survives. The holdout is ~25% weaker than reported** (+0.066 ->
+0.050); gross is unchanged at +0.089 / +0.102, so only the running cost
moved, not the signal. **Treat +0.050 as the honest holdout number.**

### Two caveats on the correction itself

* The spread field is **zero on 16.7% of bars and on 75% of 2019-2020**. A
  broker spread of exactly zero is not credible - the field is unpopulated.
  Those were treated as unknown rather than free, which is why the dev cost
  of 0.0044 rests on the 65% of trades that are populated and is probably
  optimistic.
* Gold before 2019 on Deriv is almost certainly backfilled from a vendor, so
  the 2011-2018 spreads are that vendor's, not Deriv's.

### Still unquantified, and adverse

**Entry slippage.** Assumed zero throughout. The first live fill slipped 1.69
price units - 4.4% of that trade's risk. The forward test measures this for
free and it is the main reason to run it.

---

---
[All findings](../../README.md)
