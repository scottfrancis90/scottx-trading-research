# Finding 74 - the gold Strategy Factory: seven runs, 62.7 million genomes, zero survivors, and one shape it will not stop finding.

`factory/` (config, data, primitives, genome, simulate, evaluate, fitness, ga,
validate, holdout, report, test_engine). Built 2026-09-26 on the user's
instruction: the GA factory, XAUUSD only. Deriv gold 2011-01 to 2026-08, split
TRAIN 7.9y / VALIDATE 3.9y / HOLDOUT 3.8y with a 20-day embargo. The holdout
has never been read.

**THE RESULT. Zero survivors, every run.** The best candidate ever produced
reached **t = 2.58** on validation against a required **4.63**. Across ~14,000
distinct genomes the expected best |t| from pure noise alone is about **4.37**,
so the search's best find is *weaker than chance would generate*. On this data,
at this search size, gold has nothing that survives the gates.

**THE SHAPE IT KEEPS FINDING.** Four consecutive runs, two vocabularies (1.8M
and 62.7M genomes) and two different fitness objectives all converged on the
same object within ten generations:

> a volatility expansion (5-bar range >= 1.25x its long median), then a
> **LIMIT order at the upper rail** -- selling the rally -- with an ATR stop
> and an R-multiple target.

It appears on M15, M30, H1 and H4 simultaneously. Validation means +0.02 to
+0.18 R on 306-682 trades, positive in nine of ten candidates, never
significant. **It is the mirror of StraddleX**, which buys the breakout and
which measures **-0.087 R (t -0.96)** on the same validation split. The
factory's persistent finding is that on gold, fading an expansion beats
following it -- consistently, and not yet provably.

To clear the corrected bar this shape would need about **2,200 validation
trades**; it has 682. That is a statement about how much evidence is missing,
not a promise that more would confirm it.

**SEVEN LEDGER RESETS, EACH FOR A REAL DEFECT** (`factory/reset_history.json`).
In order: indicators computed per-slice so the same bar read 1.259 on the full
series and 1.009 in the validation slice; higher timeframes grouped by row
count instead of the calendar; no minimum R, so the GA found a stretch where
gold's ATR collapsed to one cent, placed a 3.2-cent stop and booked **+584 R on
a single trade** that carried +2.94 of a +3.11 R average; inverted and shuffled
controls that scored a *different, smaller sample* than the rule (68 and 170
trades against 250), which inverted their verdicts; and a fitness function whose
flat small-sample penalty let the GA maximise luck -- its top twenty genomes all
had **152-164 trades against a 150 floor** while the median genome had 537.

Bonferroni is charged against **ledger x resets**, because throwing away the
record of a search does not undo the search. The candidate fails at every
correction including none at all being applied to the reset count.

**WHAT THE MACHINE IS WORTH.** It caught five defects in its own measurement
before any of them reached a conclusion, including three that had produced
apparently excellent results. The engine gate (random entries must return minus
the cost; five hand-built trades must match arithmetic worked out by hand) is
what caught the first, and is the reason to trust the null.

**KNOWN GAP, recorded not fixed** (`factory/ARCHITECTURE.md`): every filter in
the vocabulary is slow -- daily bias, swing structure, session, ATR band.
Nothing asks what price is doing *at the moment of entry*, so a genome can fill
a long into a bar that is selling hard because its definition said buy. Raised
by the user, deferred by the user. Any future survivor carries the caveat that
it was never asked to check the immediate tape.

**Nothing built. The holdout is unspent.**

---
[All findings](../README.md)
