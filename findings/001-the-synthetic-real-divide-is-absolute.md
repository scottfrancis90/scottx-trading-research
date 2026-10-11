# Finding 1 - the synthetic/real divide is absolute

Four measurements separate synthetic from real instruments with **no overlap
whatsoever**. Not a difference of degree.

| measurement | synthetics (45) | real (3) |
|---|---|---|
| volatility clustering, AC(1) of \|return\| | max **0.0058** | min **0.2266** |
| time-of-day dispersion, max/min mean \|return\| by hour | max **1.16** | min **3.00** |
| continuity against a 24/7 clock | min **0.9999** | max **0.6850** |
| excess kurtosis (Volatility group) | max **0.03** | min **110.6** |

The absence of volatility clustering is the sharpest of these. Every real
financial series ever measured has it; it is the most robust stylised fact in
the field. The Deriv synthetics have **none** - |return| autocorrelation is
zero to three decimal places. Volatility on these instruments is a constant
parameter, not a state variable.

The clock result says the same thing from another direction: an hour of the
day means nothing to a synthetic (dispersion 1.03-1.16, which is sampling
noise) and a great deal to AAPL (5.35), MSFT (6.27) and gold (3.00).

**Consequence for any later work.** Every technique that earns its keep by
modelling *changing* volatility - GARCH, volatility regimes, ATR-scaled
sizing, session filters, "wait for the volatile hour" - has nothing to model
on a synthetic. That is not a claim that synthetics are unpredictable; it is
a statement that one specific and very popular family of edges is definitionally
absent.

---

---
[All findings](../README.md)
