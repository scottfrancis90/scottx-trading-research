# Finding 75 - the gold factory produced a survivor, and it passed a pre-registered holdout.

> **WITHDRAWN 2026-09-27 - see Finding 77.** The measured numbers below
> depend on lookahead in the signal generator, not on a tradable edge. Every
> implementable version of this rule loses money on TRAIN. Nothing below should
> be used, quoted, or built on.

`factory/`, run `gold_20260926T232700`, holdout lock
`factory/locks/holdout_74adf65362d23262.json`, sha 87acaa55f47a327f.
The second thing in this project's history to clear a pre-registered holdout,
after Finding 20.

**THE RULE, in full. There is nothing omitted.**

> On XAUUSD H1: take the lowest low of the previous 20 bars. Place a BUY LIMIT
> there. If filled, stop 1.5 ATR below the entry, target 3 R above it, and
> close at market after 20 bars either way. No filter, no session, no
> structure condition, no trend check. About 10 trades a month.

**THE THREE SPLITS.** Boundaries fixed before the search; 20-day embargoes;
the holdout was read exactly once, after the prediction was frozen.

| split | period | n | mean R | t | halves |
|---|---|---|---|---|---|
| TRAIN | 2011-01 - 2018-11 | 994 | +0.2490 | +4.68 | - |
| VALIDATE | 2018-12 - 2022-10 | 453 | +0.3961 | +5.29 | +0.432 / +0.360 |
| **HOLDOUT** | **2022-11 - 2026-08** | **460** | **+0.3940** | **+5.09** | **+0.384 / +0.404** |

Holdout total +181.3 R, max drawdown 13.4 R, **R/DD 13.5**. Exits: 51% stop,
24% target, 25% timeout. Median R is 30 spreads, so costs are ~3% of R.

**THE PRE-REGISTRATION.** The user supplied the mechanism in their own words
before the split was touched -- "gold dips get bought, and the 20-hour low is
a reasonable place for buyers to step in" -- and a deliberately conservative
range of **+0.20 to +0.30**, explicitly because neither of us trusted the
train-to-validation improvement. It came in at +0.394, ABOVE the band, so the
verdict is recorded as PASSED (outside the predicted band) rather than a clean
hit. `holdout.py` refuses "the GA found it" as a reason by literal string
check, and the family's lock is now written; the split is spent.

**WHAT IT SURVIVED BEFORE THE HOLDOUT.** Bonferroni over **16,218** (1,802
genomes x 9 ledger resets): needed |t| >= 4.67, got 5.29. Inverted mirror
-0.7122 on the same trades at the same fills (edge +1.108). Shuffled direction
-0.2451. Plateau 100% of six one-grid-step neighbours positive. Classified
DISCOVERY -- one slot of four matching anything already known.

**THE CONTROL THAT MATTERED MOST.** The rule is long-only on an asset that
rose from $1,400 to $3,400 across the sample, so drift is the obvious
explanation. A RANDOM LONG-ONLY bracket with identical geometry (1.5 ATR stop,
3 R target, 20-bar timeout) returns **-0.133 on train and -0.054 on
validation**. The rule beats it by +0.382 and +0.450. Gold's drift does not
pay for this bracket; something about the 20-hour low does.

**AND IT IS NOT A BULL-MARKET ARTIFACT.** 12 of 12 years positive across train
and validation, including **2013 when gold fell 27.9%** (+0.234) and 2015's
-10.4% (+0.085). On the holdout, all five years positive, including 2022
(gold -0.3%, rule +0.685) and 2026 to date (gold +2.5%, rule +0.247).

**FOUR THINGS THAT ARE STILL WRONG WITH IT.**

1. **Train is the WORST split** (+0.249 against +0.396 and +0.394) and I cannot
   explain why. Out-of-sample should degrade. Every year is positive in every
   split, so it is not regime. An unexplained asymmetry in the favourable
   direction is the shape a subtle bug takes, and this session produced nine.
2. **It has no entry-momentum check.** The user raised this before the run:
   "you cant enter a buy when you see market is selling ... because you
   definition say buy then you buy which is not good." Every filter available
   was slow. This rule buys a level with no idea what the tape is doing.
   Recorded in ARCHITECTURE.md; the survivor carries the caveat.
3. **Nine ledger resets.** The true search burden is larger than 16,218,
   because each reset discarded the record of a real search. The correction it
   cleared is therefore a floor, not a ceiling.
4. **It has never traded a live tick.** Everything above is history.

**NOTHING IS BUILT YET.** No EA, no live risk. The next step is a forward test
on bars that do not exist, which is the only test left that this result has
not already passed.

---

---
[All findings](../README.md)
