# Finding 5 - no free drift anywhere

Boom is supposed to drift down between its up-spikes; Crash the reverse. Across
all 20, the mean bar return is statistically indistinguishable from zero: only
Boom 100 (t = −2.08) and Boom 99 (t = +1.97) reach |t| ≈ 2, and across 48
symbols that is precisely what chance delivers. The same holds for the 25
Volatility indices and, over this short window, for the three real assets.

**These are martingales.** The spike and the drift cancel by construction, which
is what a fair generator is required to do. Any directional claim on a synthetic
must be scored against zero, and there is no buy-and-hold drift to piggyback on
- unlike gold in the 2016-2021 sample, where +40% of training-period drift
cleared the cost bar on its own.

---

### Follow-up: the drift claim pushed on deliberately, group by group

The above was challenged on the reasonable grounds that Boom 99 (t = +1.97) might
be the one instrument that does drift. Three further checks, all on the same
run:

**Volatility, all 25.** Zero exceed |t| = 2 on M1 where chance expects 1.25; one
does on M5 (Volatility 10 Index, t = +2.16) - but that same instrument reads
t = −0.20 on M1, the wrong sign, on a window the M5 sample contains. Of the nine
nameplates existing in more than one implementation (standard / (1s) / High
Frequency), **five disagree in sign between implementations**. The family mean
drift is **+5.10 bp/day on M1 and −5.08 bp/day on M5** - equal and opposite on
nested windows, which is what pure sampling noise looks like.

**Crash, all 10.** On M1, 9 of 10 are negative, sign test p = 0.021 - the one
genuinely suggestive pattern found anywhere in this study. It does not survive:
on the longer M5 window, which contains the M1 window, it is 6 of 10 and
p = 0.754. Mean t is −0.44, max |t| is 1.76, and none exceeds 2. The sign test
also assumes the ten series are independent, which is unverified and probably
false. **Recorded as looked-for, found, and failed on the out-of-window check.**

**The decisive one.** Boom 99 and Boom 100 are structurally near-identical
(5.06% vs 4.94% vol, 362 vs 374 jumps/day, skew +1.86 vs +1.90) and their drift
contradicts on *both* windows:

| | M1 | M5 |
|---|---:|---:|
| Boom 99 | **+1.97** | **+2.27** |
| Boom 100 | **−2.08** | **−2.47** |

Both cannot be real. This is 40 cells (20 instruments × 2 windows) producing a
maximum |t| of 2.47, which is unremarkable, and the largest values landing on a
pair that disagrees with itself.

The one thing that repeats rather than contradicts is that **Boom 100 and
Crash 100 are both negative on both windows** (|t| 1.76-2.47). Out of 40 cells
that is not yet evidence, but it is the single cell the H1 pass should look at
first.

Caveat on method: half of all movement in these instruments arrives in rare
jumps, so the t-statistic's normal approximation is optimistic here. If
anything, these t-values overstate significance rather than understate it.

---

---
[All findings](../README.md)
