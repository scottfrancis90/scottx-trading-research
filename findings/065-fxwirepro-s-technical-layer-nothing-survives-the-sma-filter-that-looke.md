# Finding 65 - FxWirePro's technical layer: nothing survives. The SMA filter that looked strongest fails on the one pair we still trade.

`fxwire_tech.py`, prereg `fxwirepro_technical_layer`. SMA(200) trend, the
Fibonacci zone of yesterday's range, and distance to prior-day support and
resistance, all measured causally at the entry bar.

**Gold straddle:** SMA alignment is backwards - with-trend +0.021,
against-trend +0.072, baseline +0.076; the control beats the filter, so it
is noise. Fibonacci: breaking **outside** yesterday's range +0.1121 (n 1,317,
t 2.66) against +0.0755 - predicted, and mechanically sensible since that is
what an expansion is - **but its first half (+0.055) is below the baseline's
(+0.066), so it fails the both-halves rule.** S/R proximity: +0.080 near vs
+0.075 clear, nothing.

**Asian range:** SMA alignment looked like the best result of the session -
skip against-trend +0.0467 (n 12,796, t 5.51) vs +0.0351, better mean in
both halves, drawdown 202.8 → 91.9, and the control clearly worse (+0.0140).
It survived the per-pair check (all three positive) and the time split
(+0.050 early, +0.020 late). **It fails the check that matters**: on USDJPY
alone - the only pair AsianRangeX now trades - 2002-2012 diff +0.082,
2013-2018 +0.082, **2019-2026 −0.065**. Since 2019 the filter keeps +0.0400
against +0.0635 for trading everything: it *costs* money, and the
against-trend group is now the better one. Pooled significance was carried
entirely by 2002-2018. **Nothing adopted.**

### Change of record - AsianRangeX 1.12, one pair
At the user's instruction (2026-09-18) `InpSymbols` goes from
`"GBPJPY,USDJPY"` to `"USDJPY"`. Not a research decision; the saved chart
input was updated to match so it survives restarts.

---
[All findings](../README.md)
