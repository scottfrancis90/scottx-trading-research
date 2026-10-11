# Finding 66 - Candle Range Theory (3-candle sweep): the pattern hits at exactly its own break-even rate, and its mirror does no worse.

`crt3.py` (prereg `crt_three_candle_sweep`, sha 855fdf54). The user's own
specification: Candle 1 sets a range; Candle 2 sweeps one extreme, closes
back inside, and closes in the sweep direction (bearish for a buy setup);
Candle 3 confirms; stop beyond Candle 2's wick; TP1 = Candle 1's midpoint,
TP2 = Candle 1's opposing extreme. 14 FX pairs + XAUUSD, H1 and H4, 25
years, one trade at a time, spread + 0.0107 R slippage, same-bar stop wins.

**The spec contains one impossibility, stated before testing:** "Candle 3
closes beyond Candle 2's close" cannot be known at "the open of Candle 3".
Both causal readings were tested - E1 (enter at C3's open, setup complete at
C2's close) and E2 (wait for C3 to close, enter at C4's open).

| H1, E1 | n | mean R | win% | half1 / half2 | R:R |
|---|---|---|---|---|---|
| the rule, TP1 | 80,381 | −0.249 | 51.3% | −0.263 / −0.234 | 0.51 |
| INVERTED control | 80,437 | −0.234 | 52.6% | | 0.51 |
| the rule, TP2 | 96,968 | **−0.189** | 45.5% | −0.208 / −0.170 | 1.19 |
| INVERTED control | 97,216 | **−0.144** | 48.5% | | 1.19 |
| NO-SWEEP control | 71,376 | −0.284 | 39.5% | | 1.38 |
| E2 (wait for C3), TP2 | 60,763 | −0.143 | 56.4% | −0.138 / −0.149 | 0.62 |

H4 is the same picture (rule −0.202, mirror −0.183).

**Why it loses, exactly.** Exits on the H1/TP2 book: 53% stop at −1.085,
45% target at +0.846, 2% time. The setup offers **1.19 R**, whose break-even
win rate is **46%**; the pattern achieves **45%**. It is a fair coin at fair
odds - then spread, slippage and stops filling past the wick (−1.085, not
−1.00) take it negative. The target's realised reward (+0.846) is below the
advertised 1.19 because near targets get hit and far ones do not.

**Controls.** Inverted (identical geometry, opposite side, each side paying
its own spread) is **better** than the rule on both timeframes: the
pre-registered bar was rule-minus-inverted > +0.05; the measured values are
−0.046 (H1) and −0.019 (H4). Direction contributes nothing. The sweep itself
is not nothing - no-sweep setups score −0.284 against −0.189 - but a real
sweep is worth about 0.10 R against a 0.19 R hole.

**Prediction scorecard:** TP1 win 60-70% predicted, 51% measured (wrong);
TP2 35-45% predicted, 45.5% measured (right at the edge); means inside the
predicted bands; INV within 0.04 R predicted, 0.046 measured (right);
NOSW within 0.03 predicted, 0.095 measured (wrong - the sweep matters more
than I expected); E2 worse than E1 predicted, E2 is **better** (wrong).

**Three harness bugs were found and fixed before these numbers, all mine:**
the inverted control re-derived its targets from C1 and so tested a
different strategy (5,799 trades against the rule's 81,679); trades were
allowed to overlap; and the mirror was priced at the rule's entry, handing
it a free spread (~0.04 R). Each fix moved the result. **Rejected; nothing
built.**

### Addendum to Finding 63 - three proposed FastX improvements, and why the one that looked real was a definition artifact

`fastx_v2.py` (prereg `fastx_three_improvements`). Baseline: FastX on the six
instruments the user named (the six that came back positive in the
per-instrument table - a reference already fitted on this data, stated
before running). 1,747 trades, +0.0514 R, 59.3% win, +89.8 R, R/DD 3.00.

| | n | mean R | win% | total R | verdict |
|---|---|---|---|---|---|
| **V1** only when EMA20 has crossed | 931 | +0.022 | 58.4% | +20.1 | fails both bars |
| V1c control: only when it has NOT | 816 | **+0.085** | 60.3% | +69.6 | passes the project's bar |
| **V2** nearest swing target, uncapped | 825 | +0.037 | **66.2%** | +30.5 | fails on total R |
| V2c control: level must exist, 1R | 1,747 | +0.051 | 59.3% | +89.8 | identical - every chapter has a level |
| **V3** best hours (chosen H1, applied H2) | 492 | +0.047 | 59.3% | +23.2 | worse than ignoring hours |
| V3c control: the *worst* hours, applied H2 | 260 | **+0.092** | 61.2% | +23.9 | beats the "good" hours |

V2 is the win-rate trap in its purest form: **+6.9 points of win rate for a
third of the profit**, because the nearest swing sits at 0.69 R against the
0.90 R the rule already uses. V3 in-sample scored +0.104 R at R/DD 5.00 - the
same selection out of sample gave +0.047 against +0.063 for ignoring hours
entirely, while the rejected hours made +0.092. Finding 51 Q3 again.

**V1c, the row that passed, does not survive.** `crossed` is a STATE
(`e20[c2] > e50[c2]`), not a crossing event, so V1c means "the EMA20 has not
yet caught up". Checks: per instrument **6 of 10** (chance); on the four
instruments never used to select anything it **reverses** (NOT −0.022 vs
crossed −0.006); by period it reverses (early +0.080, late −0.030). And the
definition test finds the cause - splitting by EMA20/EMA50 separation:
tangled (< 0.15 ATR) diff **+0.075**, 0.15-0.5 ATR **+0.005**, > 0.5 ATR
**+0.023**. The entire effect sits where the two averages are touching and
the label is a rounding decision rather than a market state.

**Nothing adopted; no EA copy made.** Prediction scorecard: V1 fails as
predicted (though the mechanism was the reverse of the stated one); V2 win
rate predicted down, measured **up** 6.9 points (wrong) while total R fell as
predicted; V3 out-of-sample within 0.02 of baseline predicted, measured
−0.016 (right) with the control not clearly worse - it was clearly *better*
(wrong direction, same conclusion).

---
[All findings](../README.md)
