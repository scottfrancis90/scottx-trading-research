# Finding 68 - CRT top-down (higher-timeframe range, H4 entry): nothing survives, and two bugs of mine had to be removed first.

`crt_td.py` (prereg `crt_topdown_h4_entry`, sha 29b6d57e). The user corrected
the construction: "4hr is entery", the range belongs to a higher timeframe,
entries are resting LIMIT orders that may not fill the same day, and "forget
about time am or pm". Findings 66/67 had taken the range and the stop from the
same timeframe, which pins the reward ratio near 1 and cannot produce the 3RR
the method claims. Rebuilt asymmetrically: D1/W1 range and target, H4 entry
and stop, H1 fills.

**THREE BUGS, ALL MINE, EACH FOUND BY A CHECK RATHER THAN BY LUCK.**

1. *Row-count aggregation.* Daily candles were built from blocks of 24 H1
   ROWS. FX data has weekend gaps, so the blocks drifted and each "day"
   straddled two or three real ones. Every range was inflated.
2. *Microseconds read as nanoseconds.* The calendar rewrite used
   `normalize().astype("int64") // 10**9`. These parquet timestamps are
   `datetime64[us]`, so that collapsed ~8 days into one id: 5,244 "H4 bars"
   existed where 51,768 should, each ~32 hours long.
3. *Intrabar lookahead at the fill.* Limit fills were detected on H4 bars and
   the trade was then walked from the START of that bar, crediting up to four
   hours of movement that happened before the order could have filled. **On
   the 3R exit this turned −0.33 R into +2.04 R** and produced a table showing
   +2.0 R a trade, 72% hit rates and 14/14 pairs positive out of sample. It
   was reported to the user before the check that killed it. Fills are now
   found on H1 and the walk starts on that same H1 bar, stop winning ties.

**Corrected result.** Settings chosen on pre-2013 FX only, applied unchanged
to post-2013:

| exit | EARLY (chosen on) | LATE (untouched) | pairs positive |
|---|---|---|---|
| 2 R | −0.105 | −0.039 | 4/14 |
| 3 R | −0.191 | −0.197 | 5/14 |
| 4 R | −0.276 | −0.178 | 3/14 |
| daily far side | −0.339 | −0.509 | 1/14 |

The plain rule with no stop buffer loses 1.18 R a trade at a 3R exit with
**0 of 14 pairs positive**. The H4 structure-shift entry, the weekly range,
and every order-resting time from 4 h to 20 days are negative.

**Frequency.** The user expected ~2 trades per pair per month and observed
that a stricter definition explains a lower count. Measured: the full CRT
confirmations fire ~8 times per pair-year; sweep-only, which reaches the
user's ~25 per pair-year, scores **−0.253 R**. Loosening the definition to
reach the wanted frequency makes it worse, which is the opposite of what
over-filtering would look like.

**Rejected.** Combined with Findings 66 and 67 - no predictive content
(MFE−MAE vs random +0.009 R, t 0.30), a losing geometry rather than a cost
problem, and every timeframe, target, entry, asset class and filter negative
- Candle Range Theory as a standalone rule is closed.

---
[All findings](../README.md)
