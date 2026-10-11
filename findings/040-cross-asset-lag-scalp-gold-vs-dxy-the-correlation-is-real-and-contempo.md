# Finding 40 - Cross-asset lag scalp (gold vs DXY). The correlation is real and contemporaneous. No lag exists.

**Date:** 2026-09-05 · `info/dxy_lag.py` · 283,124 aligned M1 bars,
2025-11-13 -> 2026-09-04, DXY reconstructed from its six ICE components
pulled as M1 from the broker.

### Geometry was dead before the data

Spec: 5-pip stop = 0.50 price units. Spread 0.32 (2016 gold) to 0.79 (2026
gold) at 1.8 bps -> **spread/risk 64%-158%** against a 3% gate. At the live
quote it is 90%. The trade cannot survive its own entry. Tested the
HYPOTHESIS anyway, since a bad stop does not make a claim false.

### The premise is TRUE

```
contemporaneous corr(gold, DXY), 5-min returns:  -0.414
```

Gold does move inversely to the dollar, strongly. This also validates the
proxy: a broken reconstruction could not produce -0.414, so the lead-lag
figures below are a real measurement and not a synchronisation artifact.

### The exploitable part does not exist

```
k min    corr(DXY 5-min move at t, gold move at t+k)
  1        -0.0106      5        -0.0227
  2        -0.0131     10        -0.0198
  3        -0.0150     30        -0.0132
```

**-0.41 contemporaneous, -0.01 predictive.** The information is in gold's
price by the time the DXY move is observable.

### The spec's own condition

DXY <= -0.1% over 5 min AND |gold 5-min move| <= 0.05%: **63 signals in 9.5
months, ~0.3/day** - not the 3/day the spec assumes, because a 0.1% DXY
move in 5 minutes is a **4.6-sigma** event (5-min sd = 0.0217%).

```
horizon   mean gold      t     win%      in $
+1min      +0.0098%   +1.19   52.4%    +0.445
+5min      -0.0172%   -0.98   47.6%    -0.779
+15min     -0.0399%   -1.29   44.4%    -1.805
+60min     -0.0649%   -1.10   49.2%    -2.931
```

Nothing significant in either direction. The best cell (+1 min, +$0.445) is
smaller than one spread ($0.450) - the insignificant drift does not even
pay for the entry.

### The stated rationale is backwards

"Fewer traders monitor multiple assets simultaneously" - enough do that the
lag is arbitraged to zero. Cross-asset lead-lag at minute resolution is one
of the most heavily mined effects in markets; finding it unexploited on a
retail feed would be extraordinary.

### Pattern across Findings 39-40

Three supplied strategies, three failures, and the FIRST thing that killed
each was `spread / risk`: VWAP scalp entry negative on its own bracket,
ORB at 32%, this at 90%. **Check spread/risk before writing any code.** It
takes one line and has now pre-empted every negative result in this file.

---

---
[All findings](../README.md)
