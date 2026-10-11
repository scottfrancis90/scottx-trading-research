# Finding 60 - The 12:00 UTC fade against the daily bias: 85% of trades reach the target and the rule loses 0.10 of a target per trade. The bias contributes nothing.

`fade1200.py` (prereg `fade1200_daily_bias`). User's rule: at 12:00 UTC
read the Francis Top-Down daily bias; if the 12:00 candle closes against
the bias, enter against the candle at its close, target = the candle's own
extreme, stop wide, EA closes at market within the spread of the target.
Claim: "never hits SL".

Bias engine replicated from the indicator (daily pivots 3/3, close-break of
the last unbroken swing, read on the closed day). M30 12:00 candle, entry
next open, spread paid, target inside 3 spreads skipped. 14 forex pairs
2002→2026 + XAUUSD 2011→2026, 31,471 trades.

| stop | win% | stop hit | mean T | h1 / h2 |
|---|---|---|---|---|
| 2T | 63% | 36% | −0.127 | −0.09 / −0.16 |
| 3T | 72% | 25% | **−0.103** (t −10.6) | −0.07 / −0.14 |
| 5T | 80% | 15% | −0.076 | −0.03 / −0.12 |
| none, 24 h | 85% | - | −0.053 | −0.02 / −0.09 |
| H1 candle, 3T | 71% | 21% | −0.041 | −0.02 / −0.06 |

Target reached 85%; the 15% that miss lose 5.6 T each. MAE with no stop:
≥ 2T in 36%, ≥ 3T in 25%, ≥ 5T in 15%, ≥ 8T in 7%. Break-even win rate at a
3T stop is 75% vs 72% achieved; at 5T, 83% vs 80% - widening the stop
raises the win rate and the break-even together. Controls: bias reversed
−0.101, no bias −0.102 - **the daily bias is not in the result**. 14 of 15
markets negative (EURCHF +0.05, t 1.8). Prediction held on every line.
**Not built, not tested in MT5** (the tester adds slippage and swap on
24-hour holds; it cannot improve a −0.10 T rule). Rejected.

### Addendum to Finding 60 - the continuation (proper test of the negative) and the nearer exits

**Continuation** (`cont1200.py`, prereg `cont1200_candle_direction`): with
the 12:00 M30 candle, stop = its other side, target 1R/2R/3R or flat. The
first run printed +0.049 R (t 12.3, both halves) for the 1R target and an
hour-shift "control" that appeared to single out 12:00. **Both were an
artefact**: on the entry bar the code paid the target before the stop when
both levels lay inside the bar (10.5% of trades, concentrated in the wide
12:30 bar). Fixed (same-bar ambiguity = stop; "skip" as the upper bound):
1R target **−0.141 R** (t −36), skip-ambiguous −0.040 (t −9.6); 2R −0.100;
3R −0.079; no target, flat 21:00 −0.047; all hours negative (−0.09 to
−0.14). Corrected on the same day; no EA was started. Lesson recorded: any
M30 test with a target and a stop must handle the same-bar case
explicitly, as `straddle_capacity.py` and `freq_structure.walk` do.

**Nearer exits** (`fade1200_near.py`, prereg `fade1200_nearer_exits`),
the user's second reading - fade against the daily bias, close sooner:
hold 1 bar −0.028 T; hold 2 bars −0.047; target ¼ candle **95% win,
−0.078 T** (no stop) / −0.196 (stop 3T); ½ candle 93% win, −0.069 /
−0.145; gold with a real M5 swing target −0.149 vs full candle −0.147.
Prediction held. The win-rate trap in its purest form. **Nothing adopted.**

---
[All findings](../README.md)
