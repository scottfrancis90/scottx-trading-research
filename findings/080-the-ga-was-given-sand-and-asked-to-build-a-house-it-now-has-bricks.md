# Finding 80 - the GA was given sand and asked to build a house. It now has bricks.

*2026-09-27. A vocabulary change, not a result. Nothing below has been validated.*

### The gap

Every gene the factory has ever had is an ATOM: a condition true on ONE bar.
The vocabulary could say "A and B are true here". It could not say **"A, THEN
B, within a window"**. Every pattern a trader names is that second thing:

    EMA cross, THEN a confirmation candle
    sweep the low, THEN reclaim it
    break structure, THEN retest the level

The user's framing: *"a real trader doesn't build strategies from atoms. They
build them from molecules -- patterns that have names."* This reverses their
2026-09-26 instruction ("Don't hard-code HH/HL into any gene, let the GA decide
the structure definition"), deliberately and on the record.

### Nine molecules, in factory/patterns.py

| molecule | the sequence |
|---|---|
| `cross_confirm` | EMA cross, then a bar closing past the cross bar's high with body >= min_body |
| `sweep_reclaim` | trades below the confirmed swing low, then CLOSES back above it |
| `break_retest` | closes through the confirmed swing, then returns to the level and holds |
| `pullback_bounce` | trend, pullback that TOUCHES the EMA without closing through it, then a bounce candle |
| `range_expand_fade` | a bar >= rel x smoothed range, then the first bar closing against it |
| `higher_low_hold` | a confirmed higher low, then the SECOND close above it |
| `level_reject` | one candle: takes the level, closes back, wick >= min_wick of its range |
| `rsi_divergence` | lower price low with a HIGHER RSI at the swing, then a close up |
| `rsi_reclaim` | RSI leaves oversold/overbought, then a close in that direction |

RSI is new as a primitive too (`primitives.rsi`, Wilder's alpha = 1/period, not
a period-length EMA -- getting that wrong shifts every threshold), and is
available as an `rsi_band` filter.

**Every molecule carries its own INVALIDATION LEVEL** -- the price that says the
idea was wrong -- exposed as a new `pattern_level` stop gene. That is a trader's
stop rather than a geometric one, which is what "sl should be that wide" was
asking for in Finding 78.

### They are causal, and that was checked before anything was measured

`factory/test_patterns.py` runs a TRUNCATION TEST: compute each pattern on the
full series, then on the series cut at bar k, and require every completion
before the cut to be identical. A pattern that peeks even one bar cannot
reproduce itself once the future is removed.

**All 9 pass at three cut points on 1,092,563 M5 bars.** This check exists
because of Finding 77, where a signal generator that looked ahead survived eight
gates and a pre-registered holdout -- the controls could not catch it because
they re-use the rule's own selected bars and inherit its selection. A new signal
generator now gets tested directly, not just gated.

Engine regression gate after the change: honest / arithmetic / Finding 20 all PASS.
Genome space 3.76 billion -> **26,907,098,400**.

### Wiring check (TRAIN only, one arbitrary exit config, NOT a result)

| molecule | n | mean R | t | win |
|---|---|---|---|---|
| rsi_reclaim | 1306 | -0.0300 | -0.87 | 41.8% |
| higher_low_hold | 1888 | -0.1087 | -3.93 | 38.3% |
| rsi_divergence | 1373 | -0.1175 | -3.75 | 38.9% |
| sweep_reclaim | 1710 | -0.1377 | -4.75 | 37.4% |
| pullback_bounce | 1760 | -0.1551 | -5.43 | 36.9% |
| cross_confirm | 1693 | -0.1678 | -5.83 | 36.0% |
| level_reject | 521 | -0.1771 | -3.30 | 34.5% |
| range_expand_fade | 1383 | -0.1804 | -5.51 | 34.7% |
| break_retest | 723 | -0.1814 | -4.03 | 35.5% |

Nine experiments, all negative, all in the ledger. One exit configuration each
says nothing about the combinations -- that is what the GA is for.

### Bonus: "why can't the GA find a 70-80% win rate?"

It can, instantly. Same entries, same stops, same bars, only the target moved:

| target | win rate | mean R | break-even needs |
|---|---|---|---|
| 0.25 R | 64.4% | -0.1805 | 82% |
| 0.50 R | **68.5%** | -0.1324 | 70% |
| 1.00 R | 52.8% | -0.1053 | 54% |
| 2.00 R | 35.3% | -0.1353 | 37% |
| 4.00 R | 26.2% | -0.1498 | 23% |

The achieved win rate always lands about two points BELOW the rate required.
That gap is the cost, and it is constant. Win rate is not information; it is a
choice of target. Finding 29 measured the same conservation law exactly:
TP 1R gave 46.16% win and TP 2R gave 30.80% win, both **-0.186172 R per trade,
identical to six decimal places.** A vendor selling an "80% win rate" is
selling the 0.25 R row.

---

---
[All findings](../README.md)
