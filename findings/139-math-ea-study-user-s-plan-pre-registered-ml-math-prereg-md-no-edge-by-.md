# Finding 139 - "Math" EA study (user's plan, pre-registered ml/math_prereg.md): no edge by the rule; one lead (2026-10-09)

ml/math_study.py (out: ml/math_study_out.txt, setups: ml/math_setups.csv). Deriv MT5
2017-2026, H1/H4/D1. BUY A + BUY B (A*B = EURCHF), SL k x ATR each; first SL = signal;
add to the survivor next open; exit +/-1 SL-distance from the add or time cap.
Q4/Q6: first SL comes fast (median 1-3 candles: 1-12h on H1/H4, 1-2 days on D1); spread
0.2-1.6% of R. Same-candle double SL ("mirror broke") 12-19% at k=0.5, 2-5% at k=1.
Q5 core, survivor win rate (break-even ~50% + spread): H1 42-47%, H4 41-48%, D1 45-55%.
Only EURUSD/USDCHF D1 k=1 beats it: 54.9% (DEV 54.7 / VAL 55.2), +0.21 R per setup,
$+668 over 9.8y at 0.01 lot, DD $125, 46 setups/yr. Cross-checks on the same D1 k=1:
EURAUD/AUDCHF -0.01 R, EURNZD/NZDCHF -0.24 R; EURUSD-alone control -0.02 R.
Q1/Q3 EURCHF state: QUIET is NOT better -- mirror breaks are MORE frequent in the quiet
quintile (H1 k=0.5: 22.5% vs 17.4%), survivor win rates flat or higher in the moving
quintiles (H4 k=1: Q1 45.8% vs Q5 49.2%). Q2: tighter mirror (corr <= -0.8 during the
setup) does NOT raise the win rate.
Pre-registered decision: EDGE requires the quiet-regime split to hold in both halves ->
FAILS. The SL hit is ~a coin flip after costs on H1/H4. D1 k=1 EURUSD/USDCHF is a lead
(1 cell of 6 primary, not confirmed by the two cross-check pairs). GA run follows.

---
[All findings](../README.md)
