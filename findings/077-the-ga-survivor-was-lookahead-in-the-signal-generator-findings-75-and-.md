# Finding 77 - the GA survivor was lookahead in the signal generator. Findings 75 and 76 are withdrawn.

*2026-09-27. Found while building the EA, by asking the only question that
matters before writing MQL5: can an EA actually place these orders?*

It cannot. The rule as measured is not implementable, and once it is made
implementable the edge is negative.

### The defect

`evaluate.build_signals` decides whether to EMIT a signal at bar `i` by scanning
bars `i+1 .. i+ORDER_LIFE` to see whether the pending order will be touched:

```python
if best is None:
    continue          # no signal at all for this bar
```

Its docstring calls this readiness/pruning and asserts it changes nothing,
because `walk()` re-derives every fill. That is false. It is a filter on the
future: *trade this bar only if the market will come back to this level within
21 bars.* For a buy limit at a 20-bar low it discards **52.9% of eligible bars
on TRAIN and 55.4% on VALIDATE**, and the bars it keeps are the ones where
mean reversion was about to happen.

### What it was worth

Same engine, same `walk()`, same costs; the only change is emitting at every
eligible bar instead of only the ones that will fill:

| | TRAIN | VALIDATE | HOLDOUT |
|---|---|---|---|
| as measured (Finding 75) | +0.2490 (t 4.68) | +0.3961 (t 5.29) | +0.3940 (t 5.09) |
| pruning removed | +0.0686 (t 1.74) | +0.1713 (t 3.00) | +0.3068 (t 4.57) |

And three genuinely implementable order models, each the EA's real behaviour:

| order model | TRAIN | VALIDATE | HOLDOUT |
|---|---|---|---|
| re-price the limit to lo20 every bar | -0.1973 | -0.0960 | +0.0171 |
| freeze lo20, rest 21 bars, never re-price | -0.1851 | -0.1385 | +0.0114 |
| freeze + rest + the 20-bar cooldown | -0.2354 | -0.1010 | -0.1841 |

Trade counts match the measured book closely (969 vs 994 on TRAIN for the third
model) but **only 24-34% of the trades are the same ones**, the win rate falls
from 43% to 29%, and targets are hit half as often (12% vs 24% of exits).

### The one causal rescue, tested and failed

The pruning is largely a PROXIMITY selector: bars it kept sit a median 1.35 ATR
above the level, bars it discarded 3.28 ATR. Proximity is knowable at the bar,
so `(close - lo20)/ATR <= thr` is a legal filter rather than a peek. Tested on
TRAIN and VALIDATE only, at thr in {0.5, 1.0, 1.5, 2.0, 3.0} and order lives
{21, 5} - **all ten combinations lose on TRAIN at t -4.41 to -5.37.** The
proximity proxy does not recover the edge, which means the pruning was
contributing more than proximity: it was conditioning on the reversion itself.

### Blast radius - Finding 20 and the live bot are NOT affected

The defect scales with how often the pending order fails to fill, because that
is when the pruning bites:

| shape | TRAIN skip rate | VALIDATE skip rate |
|---|---|---|
| `fade_level` H1 (the survivor) | 52.9% | 55.4% |
| `break_level` M30 (StraddleX, Finding 20) | **0.2%** | **0.1%** |

A breakout straddle puts its rails either side of price and is touched almost
immediately, so the pruning discards nothing. **Finding 20, the Deriv straddle
forward test and the live bot are unaffected.** Any factory result built on
`fade_level`, or on any pending order that frequently fails to fill, is
contaminated and must be re-measured with the pruning removed.

### What this costs

* Findings 75 and 76 are withdrawn. No EA was built; no money was risked.
* The H1 holdout was spent on a contaminated hypothesis. It cannot be reused.
  The Dukascopy history back to 2004 is unseen but is explicitly not a holdout,
  and using it now as one would be choosing a test after seeing this failure.
* Eleventh defect caught in-harness, and the first to survive all eight gates
  AND a pre-registered holdout before being caught. **A holdout confirms
  whatever the harness computes, including its errors.** The random-entry
  control is the guard against a wrong measurement, and it did not fire here
  because the defect is in signal SELECTION, not in fill arithmetic - the
  control re-uses the rule's own selected bars, so it inherits the same
  selection. That is a gap in the control design, not bad luck.

**Status: no tradable rule. The factory's fade shapes need re-measuring.**

### Fixed, and the formal verdict

`evaluate.build_signals` now uses the forward scan only to choose WHICH rail of
a two-sided order fills first, never to discard a bar. A one-sided order is
emitted every eligible bar and `walk()` settles the fill causally. The cooldown
(`last_exit`) is charged only for a signal known to become a trade; otherwise
`walk()`'s `one_at_a_time` owns the blocking from the real exit bar. The
two-sided code path is bit-identical to before, so no breakout result moves.

Engine regression gate after the patch: **engine-honest PASS, arithmetic PASS,
reproduces Finding 20 PASS.**

Re-gating the survivor on the corrected engine:

```
  [PASS] trades on validation                  n=780
  [PASS] both halves positive                  +0.2501 / +0.0926
  [FAIL] Bonferroni over 16,218 (1,802 x 9)    t +3.00, need |t| >= 4.67
  [PASS] inverted control loses                mirror -0.5157, edge +0.6870
  [PASS] shuffled direction is flat            -0.1955
  [PASS] plateau on validation                 100% of 6 neighbours positive
  [PASS] collapse / improvement / discovery    DISCOVERY (closest: StraddleX, 1/4)
  VERDICT: DEAD
```

It fails the multiple-testing gate it originally passed, which is the correct
outcome: t 3.00 against 16,218 distinct genomes is noise. Under the corrected
engine this rule would never have reached a holdout at all.

---

---
[All findings](../README.md)
