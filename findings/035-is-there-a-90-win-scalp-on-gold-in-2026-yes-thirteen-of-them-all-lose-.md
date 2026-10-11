# Finding 35 - Is there a 90%-win scalp on gold in 2026? Yes, thirteen of them. All lose money, and none beats random entry.

Asked directly: find a scalp that works 90% this year. Both halves of the
answer are in the title.

### Design, fixed before the run

"Find what worked this year" is the search Finding 34's chase test showed is
a lottery, so 2026 was cut in two and the champion measured once on the far
half:

    DEV  2026-01-01 -> 2026-04-30    search here
    VAL  2026-05-01 -> 2026-08-31    measured ONCE

    PASS = the DEV champion is net positive on VAL after cost.

Six families, all standard, none invented for this test: N-bar breakout,
N-bar fade, RSI(14) 30/70, EMA9/21 cross, Bollinger(20,2) fade, and
**random entry as the null**. Stop 2 x ATR(14) throughout so R is comparable;
target swept 0.10 -> 4.00 x ATR, which is the dial that buys the win rate.
Max hold 60 bars. XAUUSD M5 and M15. 72 cells.

### The 90% is real and it is free

Thirteen cells cleared 90% on DEV. **Every one of them sits at TP = 0.10 x
ATR** - the target parked next to the entry.

    M5     family  TP     dev win    dev net      val win    val net
           EMA    0.10     94.0%     -0.0264       93.9%     -0.0312   FAIL
           BRK    0.10     93.7%     -0.0290       94.0%     -0.0298   FAIL
           RAND   0.10     93.1%     -0.0359       92.8%     -0.0431   FAIL
           FADE   0.10     92.6%     -0.0399       93.5%     -0.0351   FAIL
           BB     0.10     92.2%     -0.0447       92.9%     -0.0411   FAIL
           RSI    0.10     91.9%     -0.0460       91.2%     -0.0574   FAIL

    M15    RAND   0.10     96.6%     +0.0062       96.0%     -0.0018   FAIL
           EMA    0.10     93.4%     -0.0270       94.0%     -0.0235   FAIL
           BRK    0.10     92.0%     -0.0411       93.0%     -0.0326   FAIL

**Not one 90% cell built from a real signal is net positive on either half.**
A 96.6% win rate appears in the table and it belongs to random entry.

The arithmetic, for the 94% EMA cell: 0.94 x 0.05 - 0.06 x 1.00 = -0.013
gross, minus 0.012 cost = -0.025. The measured value is -0.0264. There is
nothing to explain; the payoff ratio decides it before the market is
consulted.

### And cost is NOT the excuse this time

    cost / risk    M5  1.2%     M15  0.7%

Both pass the 3% gate comfortably, because a 2 x ATR stop is wide enough to
carry the spread. Unlike Findings 25, 27, 28, 29 and 31, these strategies
are not being killed by cost. **They simply have no edge.**

### The null wins

    M5   best DEV cell by expectancy   RAND TP 2.00   dev +0.0382 -> val +0.0102
    M15  best DEV cell by expectancy   RAND TP 4.00   dev +0.2295 -> val -0.0870

On M5 the DEV champion across all 36 cells **was random entry**. No family
beat coin-flip entries on either timeframe.

The M15 random cell is the whole study in one line: **+0.2295 R on DEV,
-0.0870 on VAL** - a spectacular in-sample champion, from pure noise,
collapsing the moment it met unseen data. That is Finding 34's chase result
reproduced inside a single test, on purpose.

### Multiple testing, stated

72 cells were examined. One cell "passed" - RAND TP 0.25 on M15, val +0.0097
on n = 149. It is a random-entry cell with the smallest sample in the table,
and at 72 draws a couple of chance passes is the expectation, not a
discovery. It is reported because hiding it would be selective, and it is
not a find.

### Verdict

**No scalp strategy was found.** A 90% win rate on gold in 2026 is available
from six different signals and from no signal at all, costs nothing to
obtain, and is worth less than nothing in every case. This is the fourth
independent measurement of the same law in this document - Finding 33, the
0.05R target sweep (88.6% hit, -0.0828 R), the session-range test (90.2% hit,
net negative), and now this.

Win rate is a dial, not a result. The straddle at 19-22% wins remains the
only thing here that has ever made money out of sample.

Script: `info/scalp2026.py`.

---

---
[All findings](../README.md)
