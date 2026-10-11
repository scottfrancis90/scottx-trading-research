# Finding 76 - the GA survivor's losers run deep into profit first, and that fact is useless

> **WITHDRAWN 2026-09-27 - see Finding 77.** The measured numbers below
> depend on lookahead in the signal generator, not on a tradable edge. Every
> implementable version of this rule loses money on TRAIN. Nothing below should
> be used, quoted, or built on.

*2026-09-27. XAUUSD H1, buy the 20-hour low, 1.5 ATR stop, 3R target, 20-bar
timeout. Realised R throughout, not intended R.*

MFE reached before the stop was hit, stop-outs only. MFE is measured over
completed bars **strictly before** the bar that hit the stop, because the stop
lands somewhere inside that bar and the high and low inside a bar cannot be
ordered - crediting the stop bar's own high would be a lookahead in the rule's
favour.

| | TRAIN | VALIDATE | HOLDOUT |
|---|---|---|---|
| stop-outs | 525 / 994 | 211 / 453 | 233 / 460 |
| reached >= 0.1 R | 72.0% | 72.5% | 74.2% |
| reached >= 0.3 R | 68.6% | 69.2% | 70.4% |
| reached >= 0.5 R | 59.6% | 61.6% | 63.5% |
| reached >= 1.0 R | 29.5% | 38.9% | 40.3% |
| reached >= 2.0 R | 5.1% | 4.7% | 9.0% |
| never positive | 27.2% | 27.5% | 24.0% |
| median MFE | 0.618 R | 0.766 R | 0.781 R |
| mean MFE | 0.723 R | 0.803 R | 0.884 R |

Permissive variant (counting the stop bar's high): never-positive falls to
0.4-1.3% and mean MFE rises to ~1.1 R. That variant is not used for any
decision; it is recorded only to show the size of the intrabar ambiguity.

**The obvious conclusion is wrong.** A breakeven stop armed at +X R was tested
on TRAIN and VALIDATE (the holdout was not consulted) and loses at every
arming level:

| arm at | TRAIN d total R | VALIDATE d total R |
|---|---|---|
| 0.3 R | -106.7 | -89.8 |
| 0.5 R | -97.5 | -81.9 |
| 0.7 R | -107.9 | -70.7 |
| 1.0 R | -63.0 | -34.4 |
| 1.5 R | -50.7 | -23.7 |

At +0.5R on TRAIN it saves 313 stop-outs but kills 99 targets **and 182 timeout
exits collectively worth +125 R**. The timeout bucket is the one the MFE table
hides: it averages **+0.868 R** and most of it dips back through entry on the
way. Damage shrinks monotonically as the arm moves later - the less the change
touches the rule, the less it costs - which is the signature of a modification
carrying no information. R/DD does not improve (8.1 to 16.1, unrelated to the
arm level).

**Mechanism.** A pullback through entry does not separate winners from losers
on this rule, because the rule buys a 20-hour low: chop around the fill *is*
the entry condition. Same reason the entry-momentum filter failed
(the tape audit, same date).

**Decision: ship plain.** No entry filter, no breakeven, no trail.

**Note on the holdout column.** The holdout was already spent by Finding 75 and
its lock is written. The column above *describes* an accepted result; it is
forensics, not a second test. No rule change may be justified on it, and none
was - the breakeven test above ran on TRAIN and VALIDATE only.

**Measurement defect found and fixed during this work:** the exit label is
`"time"`, not `"timeout"`. The first version of the breakeven attribution
matched `"timeout"` and reported "0 timeouts killed", which concealed the
entire mechanism. The R arithmetic was unaffected; the explanation column was
not. Tenth defect caught in-harness.

---

---
[All findings](../README.md)
