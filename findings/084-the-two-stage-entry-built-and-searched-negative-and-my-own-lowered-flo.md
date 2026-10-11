# Finding 84 - the two-stage entry built and searched. Negative, and my own lowered floor manufactured the false positive.

*2026-09-27. Pre-registered in `factory/runs/PREREG_chapters.md` before the run.
Entry slot restricted to chapters. Ledger 6,535 -> 7,795. 44 minutes.*

### What was built

`factory/chapters.py`: chapter -> zone -> rejection -> entry, from the user's
description of how they actually trade. A signal no longer IS the entry -- it
sets a DIRECTION and opens a window. A zone is a CONFIRMED swing that has not
been taken ("not the last one because is been taken"). Rejection is required;
reaching the zone is not enough. The stop is the rejection extreme plus a
buffer, never a chosen number ("good entry give you good SL").

Four rejection genes so the GA searches the DEFINITION: wick, close_back,
displace, engulf. All four pass the truncation test (`test_chapters.py`).
On H1, **92-98% of chapters produce no trade at all**, which is the point.

Two things the user found that were fixed as a result:
* **Timeout was in BARS.** 100 bars is 8 hours on M5 and 16 days on H4, yet
  crossover and mutation moved it as one quantity. Now HOURS, grid
  [8, 24, 72, 200, 480] spanning their own three cases (M1 500 bars = 8h,
  H1 200 bars = 200h, D1 20 bars = 480h).
* **The signal COOLDOWN is a separate thing from the hold.** GenomeX's
  "Timeout, bars" does both jobs (`busyUntil = bar_index + timeoutB`), and the
  effect they valued -- "it help to remove nonsense trade" -- was the blocking.
  Measured on M15: cool 0/24/72h gave +0.2305/+0.2510/+0.2760 on fewer and
  fewer trades. Their observation was correct and is now its own gene.

### Result: no survivors, and a total collapse

12 of 12 candidates identical: `H1|round_number|range_expand_fade|rejection|
r_multiple`. A further 12 were dropped as DUPLICATE TRADE BOOKS by the
dedupe added in Finding 82 -- that fix works.

Top candidate: TRAIN n=189 mean **+0.4275**. On VALIDATE: halves
**-0.2417 / -0.2584**, t **-1.70**, plateau **0% of 10 neighbours positive**,
and the inverted control **failed with the mirror at +0.1210 against the rule,
edge -0.3712**. The mirror makes money and the rule loses.

### The pre-registered prediction FAILED, and that is the result

The prereg said: *"The mirror edge stays positive. This is the one thing that
has looked different from every other family tested. If chapter candidates come
back with rule-minus-mirror near zero, the structure is another coin flip and I
should say so rather than retry with new parameters."*

It came back **negative**, which is worse than zero. By the rule written down
before looking: the structure is not carrying directional information, and it
does not get retried with new parameters.

### I manufactured this candidate by lowering the floor

`MIN_TRADES` is 400. No chapter genome reaches it on gold at any timeframe --
the most any configuration managed was 255, because the method is selective by
construction. I lowered the chapter floor to **150**, documented the risk in
`fitness.py`, and wrote: *"at 150 trades a mean of +0.25 R carries a standard
error around 0.13, so a genome can look strong on luck alone."*

That is exactly what happened, on the very next run. A 189-trade spike scored
+0.4275 and led the population. At the 400 floor it would have hard-failed and
never been seen.

The gates caught it, so nothing was built. But the deeper problem is not that
one candidate slipped through: **at 150-250 trades, TRAIN fitness is noise, and
TRAIN fitness is what the GA optimises.** The search cannot climb a signal it
cannot measure, so it climbs sampling error instead. That is not a defect in
the chapter idea -- it is a statement that the chapter method cannot be SEARCHED
on gold alone at the frequency it produces.

### Also tested and negative: the hour concentration

Chapter entries cluster hard by hour -- H1 busiest 13:00 (91 entries) against
20:00 (6), z = +8.6 at 13:00, +7.5 at 12:00, +7.3 at 06:00. Real, and not an
artifact of where bars exist. It is also not new: Finding 29 already recorded
12:00 UTC as the best hour of 24 on gold.

Used as a filter it **loses**, in all four pairs on both splits:

| tf / hold | all hours | 06-14 only |
|---|---|---|
| M5 2h VALIDATE | -0.1085 | -0.1658 |
| M5 8h VALIDATE | -0.0518 | -0.1980 |
| M15 2h VALIDATE | -0.0927 | -0.0998 |
| M15 8h VALIDATE | -0.0649 | -0.1268 |

The hours are where signals HAPPEN, not where money is. Frequency was 0.3-0.9
trades a week against the 5-6 hoped for.

**Status: no tradable rule. The two-stage structure is built, causal, and
measured negative.**

---

---
[All findings](../README.md)
