# Finding 5b - instrument age is the hidden variable, and it settles the drift question

Switching the analysis frame to M30-and-up exposed something the M1/M5 pass had
completely concealed: **Deriv's synthetics have staggered inception dates
spanning seven years, and several of the most-traded ones are months old.**

| inception | age | instruments |
|---|---:|---|
| 2011-01-02 | 13.2 yr | XAUUSD |
| 2019-01-01 | 7.7 yr | Volatility 10, 25, 50, 75, 100 Index |
| 2019-04-17 | 7.4 yr | Boom/Crash 1000 |
| 2019-05-28 | 7.3 yr | Step Index |
| 2019-07-12 | 7.1 yr | Boom/Crash 500 |
| 2019-09-24 | 6.9 yr | Volatility 10 (1s), 100 (1s) |
| 2020-06-03 | 6.2 yr | Volatility 25/50/75 (1s) |
| 2021-07-30 | 5.1 yr | Boom/Crash 300 |
| 2022-12-21 | 3.7 yr | Volatility 150/250 (1s) |
| 2024-08-30 | 2.0 yr | Boom/Crash 600, 900 |
| 2025-01-31 | 1.6 yr | Volatility 15/30/90 (1s) |
| 2025-09-03 | 0.7 yr | AAPL.OQ, MSFT.OQ |
| 2025-09-19 | 0.9 yr | Boom/Crash 150 |
| 2025-12-24 | 0.7 yr | Boom/Crash 50 |
| 2026-02-13 | 0.5 yr | Volatility 15, 30, 90 Index |
| 2026-03-19 | 0.5 yr | High Frequency Vol x5 |
| **2026-05-20** | **0.3 yr** | **Boom/Crash 99, 100, 200** |
| 2026-07-17 | 0.1 yr | Crash Boom Flip 1000 |

Boom and Crash of the same N **always share an inception date**. Independent
confirmation that each pair is one generator with a sign flip (Finding 3).

### Consequence 1 - the Boom 99 drift was measured on a 103-day instrument

Boom 99 and Boom 100 did not exist before 2026-05-20. Their M1 (69 days),
M5 (102), M30/H1/H4/D1 (103) are **the same 103 days at different
resolutions**, not independent windows. The earlier M1-vs-M5 comparison was
therefore a much weaker cross-check for these two than it was for the
volatility family, and that should not have been presented as if it were the
same test. The valid cross-check was always Boom 99 against Boom 100 - two
separate instruments over the same 103 days, drifting in opposite directions.

### Consequence 2 - the multi-year test, run properly

Year-by-year drift t-statistic on D1 log returns, for the eleven instruments
old enough to support it:

| | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Boom 1000 | −0.05 | +0.20 | +0.84 | −0.58 | +1.26 | +1.59 | −0.96 | −0.72 |
| Crash 1000 | +0.52 | +0.34 | −1.98 | −1.15 | +0.17 | −0.45 | −0.76 | +1.37 |
| Boom 500 | +0.01 | −1.19 | −1.24 | −0.79 | +0.89 | +0.92 | −0.49 | −0.81 |
| Crash 500 | −0.10 | −0.54 | −0.39 | −1.52 | −1.28 | +0.71 | −0.35 | −1.02 |
| Boom 300 | - | - | −1.12 | −1.01 | −0.32 | −0.50 | +1.32 | −1.92 |
| Crash 300 | - | - | −0.43 | −0.73 | −0.09 | +0.29 | −0.84 | −0.12 |
| Volatility 10 | −0.86 | −1.67 | −0.09 | +0.98 | +0.17 | −0.79 | −0.97 | **−2.38** |
| Volatility 25 | −1.26 | +0.54 | −0.66 | −1.43 | +1.16 | +0.21 | +0.15 | +0.66 |
| Volatility 50 | +0.25 | −0.34 | +0.52 | −0.24 | +0.51 | +0.25 | −1.74 | −0.90 |
| Volatility 75 | +1.72 | +0.68 | +0.26 | −1.17 | +0.07 | −1.61 | −1.14 | +0.22 |
| Volatility 100 | −0.88 | +0.43 | +1.42 | −0.58 | −0.79 | −0.40 | −0.86 | −0.15 |

**84 year-cells. One exceeds |t| = 2, where chance expects 4.2** - and that one
(Volatility 10, 2026) falls in a partial year.

Every instrument changes sign between two and five times across its life. Not
one holds a drift direction. Boom 1000 is positive in 4 of 8 years, Crash 1000
in 4 of 8, Volatility 25 in 5 of 8 - coin flips.

**This is the confirmatory test the drift question needed, and it is negative on
seven years of data.** The generators are martingales, as their construction
requires. The same conservatism noted in Finding 7 applies - observing 1 where
chance expects 4.2 means the yearly cells are not independent and the t is
conservative - so read this as "no drift, robustly", not as a calibrated count.

---

---
[All findings](../README.md)
