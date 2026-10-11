# Finding 2 - the Volatility indices are named after their volatility, exactly

Annualised volatility measured from M1 log returns, against the number in the
symbol name, across all 25:

**Maximum absolute error 0.42%. Mean absolute error 0.145%.**

Volatility 5 Index → 5.0003. Volatility 10 → 10.010. Volatility 75 → 74.994.
Volatility 100 → 99.980. Volatility 250 (1s) → 250.65. The worst case in the
whole group is Volatility 30 (1s) at 30.126 against 30.

This also fixes the annualisation convention: the nameplate reproduces only
under **24/7 calendar-time annualisation** (1,440 bars/day × 365), which is
the convention used throughout this study.

The `(1s)` and `High Frequency` variants differ in tick rate, not in
volatility - Volatility 10 Index, Volatility 10 (1s) Index and High Frequency
Vol 10 Index all measure 9.99-10.04.

---

---
[All findings](../README.md)
