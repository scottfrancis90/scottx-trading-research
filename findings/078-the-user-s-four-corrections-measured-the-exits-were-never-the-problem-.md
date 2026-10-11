# Finding 78 - the user's four corrections, measured. The exits were never the problem; the entry is a coin flip.

*2026-09-27. XAUUSD M5, one trade a day, TRAIN + VALIDATE only. The M5 holdout
is untouched.*

After reading the GA's trades on a 5-minute chart through GenomeX, the user made
four corrections. The rule they were looking at, from the indicator's own label:

```
SHORT  prior_range -> ema_cross | htf_structure | stop other_side | tgt r_multiple
```

Their words, and what each maps to:

| the critique | the change |
|---|---|
| "the rule is only one trade a day on 5min" | M5 + `one_a_day` |
| "sl should be that wide" | `structure` stop, behind the protective swing |
| "how can it set tp that far dont it see structure?" | `structure` target, nearest opposing swing |
| "how can GA enter in a range better wait for clean structure to form" | `not_ranging`, efficiency >= 0.25 |

Every parameter fixed once before looking: EMA 50, prior_range 100, pivot 5,
buffer 0.3, cap 3R, efficiency 0.25 over 50 bars. `htf_structure` no longer
exists - it was replaced by `swing_flags` at the user's own instruction - so the
baseline carries no filter.

### The complete factorial. All eight cells, not the best five.

| | TRAIN | VALIDATE | exits (train) |
|---|---|---|---|
| A none | -0.0726 (t -3.20) | -0.1102 (t -3.28) | stop 34% / tgt 5% / time 61% |
| B stop | -0.1276 (t -4.84) | -0.1403 (t -3.63) | stop 47% / tgt 8% / time 45% |
| C target | -0.1536 (t -6.11) | -0.0989 (t -2.81) | stop 33% / tgt 43% / time 24% |
| D range | +0.0065 (n=183) | +0.0225 (n=89) | stop 22% / tgt 4% / time 73% |
| F stop+target | -0.1899 (t -7.34) | -0.1573 (t -4.35) | stop 38% / tgt 44% / time 19% |
| G stop+range | -0.0267 (n=101) | +0.0720 (n=65) | stop 36% / tgt 6% / time 58% |
| H target+range | 24 trades | 8 trades | too few |
| E all three | 27 trades | 12 trades | too few |

### The user's diagnosis was right; the remedy does not pay

The target fix does exactly what their eye said it should: target hits go from
**5% to 43%** and the win rate from 41% to 51-56%. The unreachable 3R target off
a full-box stop was real. **And the mean gets worse anyway.** The stop fix raises
stop-outs from 34% to 47%. Each correction slides the rule along the break-even
line - win rate traded against payoff - without moving expectancy.

The only non-losing cells are D and G, and both are small (183 and 101 trades).
D was put to its control: a random 183-trade subsample of A. D's mean sits at the
**86th percentile on TRAIN and the 88th on VALIDATE** - inside the random spread.
It thinned the sample; it did not select. Its TRAIN halves are +0.1433/-0.1289.

### Why no exit could have worked

The rule's own trades, same bars, same fills, same R, same reward distance,
direction flipped:

| | rule | mirrored | coin-flip | rule - mirror |
|---|---|---|---|---|
| A TRAIN | -0.0726 | -0.1173 | -0.1186 | +0.0447 |
| A VALIDATE | -0.1102 | -0.0721 | -0.1280 | **-0.0381** |
| C TRAIN | -0.1536 | -0.0531 | -0.1022 | -0.1005 |
| C VALIDATE | -0.0989 | -0.0474 | -0.0467 | -0.0516 |

**The edge over its own mirror changes sign between TRAIN and VALIDATE**, and on
C the mirror is better on both. Both directions lose, by roughly the cost. The
EMA-cross entry carries no directional information on gold M5, so no stop, no
target and no filter can produce a positive expectancy from it.

**Status: the GA's rule is dead on M5 too, and patching its exits is finished.**
What has never been encoded is the user's OWN entry - the thing they do by eye.
The rule tested here is the GA's, which they were criticising, not theirs.

---

---
[All findings](../README.md)
