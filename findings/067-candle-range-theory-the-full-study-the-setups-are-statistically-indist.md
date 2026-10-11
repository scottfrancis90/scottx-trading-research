# Finding 67 - Candle Range Theory, the full study: the setups are statistically indistinguishable from random entries, and every knob only moves the loss closer to zero from below.

`crt_rr.py` (prereg `crt_fixed_rr`, sha ec1afe78) and `crt_study.py` (prereg
`crt_full_study`, sha bababeba). Follows Findings 66. The user supplied a
reading list (TradingView CRT H4 / NomadaScalper / SATTAM, MQL5 CTR H4 Base
Arrow and CRT Model 1, the crt-turtlesoup-ea and STAR-EA repos, FX.co and
Forex-Station), two of their own 4H charts (`crt/*.webp`, GBPUSD and JP225),
and three claims: CRT works on H4, entries come as limit orders that may not
fill the same day, it works with top-down analysis, and it wins at least 3RR.
All four were tested. ~80 comparisons; Bonferroni applies throughout.

**1. The user's 1:2, which Finding 66 never measured.** H1, 2R fixed:
−0.192 R, 30.0% win against a 35% break-even. Every multiple from 1R to 3R
loses on both H1 and H4, and the inverted mirror is **better at every one**
(rule-minus-mirror −0.050 to −0.055 on H1).

**2. Where the money goes - this is the finding.** The same H1 trades priced
four ways:

| | mean R |
|---|---|
| ideal fills, zero cost (the pattern itself) | **−0.1217** |
| + stops and targets filling where they fill | −0.1247 |
| + spread and slippage | −0.1802 |

Execution costs 0.058 R. **The pattern costs 0.122 R.** CRT is not a good
idea with an execution problem; it is a losing geometry.

**3. Does it predict anything? No.** 286,485 setups, H1 FX, MFE and MAE over
the next 24 bars in units of R, against random entries drawn from the same
bars with the same R distribution and random sides:

| | MFE | MAE | MFE−MAE |
|---|---|---|---|
| CRT setups | 5.88 R | 5.90 R | −0.021 |
| random entries | 6.42 R | 6.45 R | −0.030 |

**CRT minus random: +0.0089 R, t = 0.30.** The setups behave like random
entries. This is the test that cannot be tuned, and it is the answer.

**4. The mechanism.** A fair 1:2 bracket stops out 66.7% of the time. CRT at
2R stops out **70%**, because the stop is parked just past a wick that price
has already proved it will reach. Pushing the stop away fixes exactly that
and nothing else - at zero cost: 0% buffer −0.113, 25% −0.071, 50% −0.055,
100% −0.039, 200% **−0.014**, with the stop-out rate falling 70% → 59%.
Every knob in this study moves the result toward zero **from below**. None
crosses it. That is the signature of no edge, not of a tuning problem.

**5. What did separate: the New York candles.** H4 re-anchored to New York
time (my earlier H4 was anchored to UTC midnight - a different set of
candles), the 1AM / 5AM / 9AM candles the literature names against the other
three, which are the control:

| | n | mean R | half1 / half2 |
|---|---|---|---|
| 1AM + 5AM + 9AM NY | 9,781 | **−0.0919** | −0.083 / −0.100 |
| CONTROL: the other three | 7,880 | −0.1928 | −0.190 / −0.196 |

**+0.101 R of separation, holding in both halves**, and it was specified by
the literature before I looked. The worst candle is 9PM NY (−0.237), the
best 1AM NY (−0.065). This is a real effect and it is reported as one - it
is simply not worth 0.09 R, which is what it would need to reach zero.

**6. The rest.** Timeframe M5 → D1: every one negative, monotonically less
bad as the timeframe rises (M5 −0.252, H1 −0.180, NY-H4 −0.137, D1 −0.091).
Top-down bias does not separate consistently (1 week +0.042, 1 day −0.027,
1 month −0.019). The **box** from the user's own charts - range taken from a
3/5/10/20-bar consolidation rather than one candle, targeting the far side -
is negative at every width (−0.120 / −0.111 / −0.083 / −0.081) even though
the far-side target averages 3.2 R to 8.8 R. Asset class: FX −0.137, gold
−0.140, silver −0.126, indices −0.127, Boom/Crash −0.061, all failing their
mirrors. **All 14 FX pairs negative individually**, best GBPJPY −0.057.
The sweep does beat no-sweep by +0.088 R after matching on R/spread decile
(raw gap +0.127, so a third of it was cost) - but it is a smaller hole, not
a profit.

**On "CRT wins at least 3RR":** tested directly. 3R fixed on NY-H4 is −0.117;
the box's far-side targets average 3.2-8.8 R and lose. Raising the reward
ratio raises the loss toward −cost, because a pattern with no directional
content pays the same cost whatever the target.

**Limitation, stated rather than buried.** The retracement entry here is a
limit at Candle 2's midpoint, which fills within one bar essentially always -
fill rate 100% at every order life from 4 h to 192 h, so the limit-life scan
answered nothing. It therefore does **not** test the user's observation that
CRT trades often arrive days later. A deeper limit - into the range body or a
named level - plus a lower-timeframe market-structure-shift confirmation, are
the two parts of the method still unmeasured. FVG-based entries were not
built: the project rules forbid fair-value-gap features outright.

**Prediction scorecard:** ideal-fill near −0.05 predicted, −0.122 measured
(wrong, and worse than expected); CRT within 0.05 R of random on MFE−MAE
predicted, +0.009 measured (right); sweep effect at least halves under
matching predicted, it fell from 0.127 to 0.088, a 31% cut (wrong - it
survived better than I expected); nothing passes the scans predicted, nothing
passed (right). **Rejected; nothing built.**

---
[All findings](../README.md)
