# Finding 91 - the high reward:risk "excess" was degenerate stops. With a minimum-R floor the effect flips sign between splits.

*2026-09-27, overnight. FX, 17 pairs, daily and H4. Holdout not read.*

### The sequence, and why it nearly became a false positive

Finding 90 measured the user's method (break -> retrace -> entry -> next pool)
at -0.8 to -1.2 pp, i.e. fair odds. One pre-declared conditioning variable was
then tested: reward-to-risk. It appeared to split the result cleanly --

| R:R | excess, all four cells |
|---|---|
| 0-2 | -26 to -31 pp |
| 8+ | **+7.3 / +8.9 / +8.9 / +8.1 pp** |

A PLACEBO CONTROL (same barrier distances, entry at a random bar) came back at
~0 pp in every bucket, so the random-walk null was sound and the effect looked
real. Expectancy was then priced with costs -- and returned **+11.47 R a trade
with a median cost of 132.8% of R**.

That is impossible, and it is what exposed the defect.

### The defect

When price retraces EXACTLY to level A, the retrace bar's extreme sits on top
of the entry, so the stop distance collapses toward zero. That inflates the
reward ratio without limit -- which is why those events filled the 8+ bucket --
and inflates the payoff on any win. A spread larger than the entire stop means
no broker would ever fill the trade.

**Identical in kind to the GA's +584 R gold trade**, where a 1-cent ATR
produced a 3.2-cent stop. The fix is the same: a minimum R of 8 spreads, as
`factory/config.py` already applies everywhere else.

### With the floor applied

| | TRAIN | VALIDATE |
|---|---|---|
| Daily R:R 8+ | **-0.2529 R** (t -1.06) | +1.8321 R (t +2.56) |
| H4 R:R 8+ | **-0.4523 R** (t -2.45) | +0.3429 R (t +2.52) |
| pooled excess | -11.42 / -17.56 pp | -2.97 / -6.84 pp |

Negative on TRAIN, positive on VALIDATE, on both timeframes. A sign flip
between splits is noise. Pooled excess is now clearly negative everywhere.

**Verdict: no edge. Finding 90's conclusion stands -- fair odds at best -- and
the reward:risk conditioning adds nothing once degenerate stops are excluded.**

### The lesson, recorded because it repeated

The placebo control PASSED and the result was still an artifact. A control that
randomises the ENTRY cannot catch a defect in how the TRADE GEOMETRY is
constructed, because the placebo inherits the same broken distances. Only
pricing the expectancy in R exposed it -- the 132.8% cost figure was the tell.

**Any probability test must be followed by an expectancy test before it is
believed.** Thirteenth measurement defect of the day.

---

---
[All findings](../README.md)
