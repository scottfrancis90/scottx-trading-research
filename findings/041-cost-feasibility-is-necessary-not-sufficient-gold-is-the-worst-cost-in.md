# Finding 41 - Cost feasibility is necessary, not sufficient. Gold is the worst-cost instrument that works.

**Date:** 2026-09-05 · `info/feasible.py`, `artifacts/feasible_m30.csv`

### Hypothesis

`spread / risk` has explained every negative result here (25, 27, 28, 29,
31, 39, 40). So screen the universe by whether an instrument can CARRY the
geometry - `cost = spread / (2 x EMA5)` against ZETA = 3% on trigger bars -
rather than by signal. A search over the constraint, with no outcome being
optimised, so it cannot be mined the usual way. 92 instruments screened on
their own per-bar recorded spread; a 2.5x stress column reflects Finding
22's measurement that broker spread runs 2-5x tighter than the market.

### Result 1 - the cheapest instruments are the ones already known to be dead

```
Boom_500 / Crash_500 / Boom_300 ...   cost 0.15-0.20%   pass@2.5x 100%
XAUUSD                                cost 2.20%        pass@2.5x  44.2%
```

The synthetics have perfect cost headroom. Finding 22 tested all 79 for
drift and carry and found nothing; the market-structure study found they
have zero volatility clustering. **Gold, the only instrument that earns,
has one of the WORST cost ratios of anything tradeable** - over half its
signals fail the gate at realistic spread.

So cost feasibility explains every failure and predicts no success. Gold's
edge comes from real volatility structure, not from cheap execution.

### Result 2 - no better home exists for this strategy

15 real-market instruments with >=40% of triggers tradeable at 2.5x
spread, run sequentially with per-bar spread x2.5 plus measured slippage:

```
XAUUSD    1286  +0.0790  t=+1.84      USDCAD   1207  +0.0020  t=+0.05
SOLUSD     811  +0.0964  t=+1.81      XAUEUR   1021  -0.0146  t=-0.31
MSFT_OQ    148  +0.0684  t=+0.53      USDJPY   1225  -0.0105  t=-0.25
XRPUSD     834  +0.0263  t=+0.52      EURJPY   1169  -0.0629  t=-1.46
GBPUSD    1269  +0.0217  t=+0.52      USDCHF   1195  -0.0733  t=-1.76
                                      AAPL_OQ   141  -0.1473  t=-1.28
positive: 6 of 15, none reaching t = 2
```

MSFT at 0.22% cost, AAPL at 0.37%, EURJPY at 0.52% - all far cheaper than
gold's 2.20%, none better. **Cost headroom does not buy edge.**

Caveat: only XAUUSD has pre-2018 data, so these are single samples, not
split tests.

### Correction to Finding 22's Result 5

SOLUSD there was -0.1422 (holdout), flagged at the time as resting on a
weekend-inflated live quote of 13.77 bps. On its own per-bar recorded
spread stressed 2.5x it is **+0.0964, t=+1.81** - the second-best
instrument in the book. The contamination warning was correct and this is
the corrected figure. Do not pull spreads near the Friday close.

### Standing conclusion

There is no undiscovered instrument for this geometry. Gold is it, and the
reason is structural rather than economic - it is the instrument where
volatility expansion is real enough to overcome a cost ratio that would
disqualify it on paper.

---

---
[All findings](../README.md)
