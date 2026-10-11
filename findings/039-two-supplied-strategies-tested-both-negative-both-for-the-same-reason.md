# Finding 39 - Two supplied strategies tested. Both negative. Both for the same reason.

**Date:** 2026-09-05 · `info/vwap_scalp.py`, `info/orb.py`
Gold M5. Two strategy documents were supplied and coded to spec, unchanged,
and backtested before any EA was written - the order the specs themselves
asked for.

### (a) VWAP + EMA Pullback Scalp - NEGATIVE

Spec: price above VWAP + EMA9>EMA21, pull back to EMA9/VWAP, trigger on
engulfing / pin bar / inside-bar breakout, stop past the pullback swing,
target 1.5R, 08:00-12:00 EST, max 3/day, 2% risk. Split pre-registered at
2026-03-01. News filter not modelled (no calendar; hand-excluding dates
after seeing results would be fitting).

```
                        n    win%    meanR      PF    final    maxDD
broker spread ALL     623   45.7%  +0.0076    1.02   0.973x    34.4%
broker spread HOLD    219   45.2%  -0.0274    0.94   0.849x    28.9%
real 1.8bps   ALL     617   44.2%  -0.0279    0.94   0.628x    52.3%
1.8bps+0.5slip        616   44.0%  -0.0363    0.92   0.567x    55.4%
```

Outcome mix, friendliest case: TP 22.3%, SL 36.1%, **session close 41.6%
at +0.090**. Gross expectancy on the TP/SL subset alone is **-0.0265 R** -
38.2% hit rate against a 40% break-even for 1.5R. **The entry loses on its
own bracket; only the forced session-close rule drags it to ~zero.** The
risk management carries the signal, not the reverse.

Spec claimed 50-60% win rate; measured 45.7%. That ~10pp gap is the whole
difference between its projected 5-15%/month and reality.

Its own 2% sizing is separately destructive on the same trades:
`0.5% -> 1.016x, 1.0% -> 1.017x, 2.0% -> 0.973x`.

### (b) Session Open Range Breakout - NEGATIVE, and diagnostic

Pre-registered primary: London open, 15-min range, stop the opposite side,
target 3R, 2-hour window, one break per session, volume confirmation.

Tested on **2016-2024 M5 (550,824 bars) never touched by this project**:

```
primary spec (vol filter)  n=1016  win 30.4%  meanR -0.1960  t=-4.18
no vol filter, 3R          n=1968  win 27.6%  meanR -0.2786  t=-8.58
years positive: 0 of 9   (2016 -0.60 ... 2024 -0.23)
```

Fading it is ALSO negative (-0.3284, t=-11.31, 1 of 9 years). Both
directions lose, which is the tell.

**At zero cost the signal is exactly neutral:**

```
GROSS  breakout 2R  +0.0085  t=+0.28
GROSS  breakout 3R  -0.0039  t=-0.11
```

The entire loss is spread. Losing 0.28 R to a 0.32 spread means average
risk is ~1.16 price units - the median 15-minute London range on gold. So
**spread is 32% of R**, against the 3% gate. Monotonic across range size:

```
range   med spread/R   pass 3%      meanR       t
 15min        31.9%       0.1%    -0.2786   -8.58
 30min        22.4%       0.2%    -0.1547   -5.08
 60min        14.4%       1.0%    -0.1185   -4.63
120min         8.8%       3.3%    -0.0595   -2.92
240min         4.8%      16.6%    -0.0092   -0.71
```

It converges to ZERO as cost falls, never to positive.

### The unifying point

ORB is Finding 20's straddle with the range set by the CLOCK instead of by
VOLATILITY, and with no cost gate. Same shape - define a range, break out,
stop the opposite side, target a multiple - and the difference in outcome
is -0.2786 R versus +0.0568 R. A fixed 15-minute window does not know how
wide gold is moving today; `2 x EMA5(range)` does, and ZETA refuses the
trade when spread is too large a share of it.

This is the sixth time `spread / risk` has explained a negative result
(Findings 25, 27, 28, 29, 31, 39). It is the number to check FIRST on any
new strategy, before writing an EA.

---

---
[All findings](../README.md)
