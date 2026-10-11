# Finding 89 - the level-to-level liquidity run: positive on daily, gone on H4 where the sample is seven times larger.

*2026-09-27. FX, 17 pairs, TRAIN + VALIDATE. Holdout not read.*

The user's model, in their words: *"each level price break that means it
targeting the other level liquidity then revser back in liquidity side"*. A
break of level A is not the trade -- it announces that price is going to the
next pool, B.

**Why this test was different from everything else today.** It is a PROBABILITY
question, not a P&L one, so it needs no stop, no target and no cost model --
the machinery that killed every other result. And it has a real null: for a
driftless walk between two barriers, P(touch B before returning to A) is
exactly `dist_A / (dist_A + dist_B)`. A 70% hit rate proves nothing if B was
three times closer. The test is the excess over that, measured per event.

Levels are swing extremes not yet taken. On the user's correction -- *"liquidity
where leg with wick you see where i draw my yellow line"* -- a level must also
carry a rejection wick of at least MINWICK of its bar's range.

### Result

| | TRAIN | VALIDATE | pairs positive (val) |
|---|---|---|---|
| Daily, no wick | +2.88 pp (n=819) | **+5.05 pp** (n=363) | 2 of 3 |
| Daily, wick >=0.3 | +3.28 pp (n=387) | **+3.21 pp** (n=168) | - |
| Daily, wick >=0.5 | +5.81 pp (n=110) | +3.23 pp (n=49) | - |
| H4, no wick | +1.39 pp (n=4,675) | **-1.18 pp** (n=2,527) | 7 of 17 |
| H4, wick >=0.3 | +2.59 pp (n=2,649) | **-0.31 pp** (n=1,345) | 7 of 17 |

Restricted to events where the next level is within 1.5x the distance of the
broken one, which is where the effect concentrates -- beyond that, geometry
dominates and the excess is +0.11 pp.

### Verdict: not established

Daily is positive on both splits, but H4 carries SEVEN TIMES the validation
sample and the effect is **gone** there: -1.18 pp, and pairs positive falls from
11 of 17 on train to 7 of 17 on validate, which is chance. Keeping the daily
result because it worked, while discarding the better-powered test, is the
selection error this project spent the whole day catching in its own code.

### What DID hold

**The user's level definition beat mine.** Requiring a rejection wick raised
the per-event excess at every threshold on both daily splits (+2.88 -> +3.28 ->
+5.81 on TRAIN). A plain 3-bar pivot fires on any local extreme including the
middle of a grind; the wick is evidence price actually reached the level and was
pushed back. The definition was right. The effect still is not there.

**And this one failed honestly.** Almost everything else today died because the
MEASUREMENT was wrong -- twelve defects, three of which had produced excellent
looking results. This hypothesis needed no fill model, no spread and no exit
rule, so there was nothing for a bug to hide in. It got a clean test and the
market said no.

---

---
[All findings](../README.md)
