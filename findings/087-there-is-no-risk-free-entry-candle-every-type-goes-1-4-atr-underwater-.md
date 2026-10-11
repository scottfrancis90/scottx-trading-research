# Finding 87 - there is no "risk-free" entry candle. Every type goes 1.4 ATR underwater first.

*2026-09-27. FX DAILY, 17 pairs, TRAIN + VALIDATE. Holdout not read.*

The user's hypothesis: *"maybe kind of candle that move that when you enter is
risk free you can hold till long days"*. Tested as MAXIMUM ADVERSE EXCURSION --
if such a candle exists, trades after it should barely go underwater, which is
what would let you hold without a stop. Five shapes declared before running,
entry at the next day's open, held 10 days, MAE in ATR units.

| candle | n (tr/va) | median MAE | MAE < 0.25 ATR | mean ret (tr/va) |
|---|---|---|---|---|
| strong body (>0.7) | 12260 / 6515 | 1.37 / 1.39 | 9% / 10% | -0.010 / -0.067 |
| big range + strong body | 5091 / 2584 | 1.32 / 1.34 | 9% / 10% | +0.038 / +0.030 |
| engulfing | 5989 / 3500 | 1.35 / 1.38 | 10% / 10% | -0.021 / +0.010 |
| outside day | 11738 / 5897 | 1.42 / 1.42 | 10% / 10% | -0.011 / +0.017 |
| close at extreme | 10951 / 5870 | 1.42 / 1.38 | 9% / 9% | -0.065 / -0.002 |

**Median MAE is 1.32-1.42 ATR for every shape, and the share of trades staying
within 0.25 ATR is 9-10% for ALL of them.** Identical across types means the
candle carries no information about which trades will stay clean.

Worse for the idea: these are HIGHER than a random entry's ~1.0 ATR MAE.
Selecting a big decisive candle selects for volatility, and volatility is
symmetric. The feature that makes a candle look convincing is the same feature
that makes the following days wilder.

**Why this matters beyond the hypothesis.** If a typical entry goes 1.4 ATR
against you before resolving, then holding without a stop means routinely
sitting far underwater. That is exactly the structure of a third-party
account examined the same day: $100 to $35,727 on AUDJPY, 14 trades, zero
losses, zero stop losses, ~1:5000 leverage, all closed in one instant. It
survives 1.4 ATR of adverse excursion because leverage and a trend covered it,
not because the entries were risk free.

**Status: negative. No candle shape gives a holdable-without-risk entry.**

---

---
[All findings](../README.md)
