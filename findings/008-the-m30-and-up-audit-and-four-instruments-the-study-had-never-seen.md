# Finding 8 - the M30-and-up audit, and four instruments the study had never seen

**Run** `artifacts/audit_20260830T185724Z` - 59 symbols x M30/H1/H4/D1 = 199
cells. Universe now read from the terminal Market Watch, equities capped at
two. One failure (Gold Basket M30).

### 8a - the Finding 1 divide classifies four unseen instruments correctly

Group medians on H1:

| kind | continuity | AC(1) of \|r\| | excess kurtosis | hour dispersion |
|---|---:|---:|---:|---:|
| volatility (25) | 1.0001 | −0.0017 | −0.02 | 1.12 |
| boom (10) | 1.0001 | +0.0036 | +0.17 | 1.16 |
| crash (10) | 1.0001 | +0.0012 | +0.24 | 1.16 |
| **flip (4)** | **1.0009** | **+0.0162** | **−0.42** | 1.60 |
| **step (1)** | **1.0000** | **+0.0147** | **+0.09** | 1.06 |
| **tactical (3)** | **0.6293** | **+0.3267** | **+42.28** | **2.49** |
| **basket (1)** | **0.6528** | **+0.3105** | **+32.34** | **3.04** |
| gold (3) | 0.6750 | +0.2796 | +26.51 | 3.08 |
| equity (2) | 0.6195 | +0.2488 | +24.71 | 6.23 |

**The `Gold RSI` Tactical indices and Gold Basket are not synthetics.** They
follow market hours (continuity 0.63-0.65, not 1.00), carry real volatility
clustering (0.31-0.33), real fat tails (kurtosis 32-42) and a real clock
(2.5-3.0). They sit with gold and the equities on every one of the four
measures, with no ambiguity.

That is a genuine out-of-sample validation: the divide was built on 45
synthetics and 3 real assets, and it classified four instruments it had never
seen without a single borderline case. It also justifies the earlier decision
to exclude them from the `gold` bucket - they are gold-derived, so they must
never be treated as an independent observation of gold.

Flip and Step fall on the synthetic side, as expected.

### 8b - Gold RSI Rebound and Gold RSI Trend Down are one series, sign-flipped

| | ann vol | skew | kurtosis | AC(1) z | jump up-share |
|---|---:|---:|---:|---:|---:|
| Gold RSI Rebound | 58.090 | **−2.3044** | 42.284 | −2.564 | 0.3184 |
| Gold RSI Trend Down | 58.084 | **+2.3054** | 42.305 | −2.560 | **0.6816** |

Antisymmetric to three decimals, and the up-shares sum to exactly 1.000. The
same mirror relationship as Boom/Crash, in a different family. **Anything
found on one must invert on the other or it is an artifact.**

### 8c - Crash Boom Flip has a STATE, which nothing else here does

| N | Flip vol | Boom N vol | Crash N vol | Flip skew | Boom skew | Crash skew |
|---:|---:|---:|---:|---:|---:|---:|
| 150 | 5.640 | 5.589 | 5.574 | **+0.002** | +0.404 | −0.426 |
| 500 | 31.607 | 30.502 | 30.607 | **+0.082** | +0.774 | −0.791 |
| 1000 | 21.918 | 21.589 | 21.607 | **+0.202** | +1.109 | −1.112 |
| 300 | 102.441 | 102.236 | 102.147 | **−0.053** | +0.586 | −0.590 |

(M30, so skew is attenuated by aggregation relative to the M1 figures in
Finding 3.)

Flip N carries **the same volatility as Boom N and Crash N** but **zero net
skew**. An instrument cannot spike only upward and have zero skew at that
volatility. So it must spike both ways - which requires a mode that switches.

**This is the first instrument in the study with any internal state.** Every
other one measured is memoryless: constant volatility, no clustering, no
clock, no regime. Flip is not.

**Do not over-read this.** Flip 1000 was created 2026-07-17 and has 45 days of
history. The skew cancellation is consistent across all four N, which is
encouraging, but confirming an actual mode - and whether the mode is
detectable in real time, which is the only thing that would matter - needs
**M1 or tick data**, because at M30 a spike is swallowed by the bar (the jump
detector finds 0.00 jumps/day for every Boom, Crash and Flip at M30). That
data has not been fetched for Flip.

### 8d - Step Index is the only non-stationary instrument found

| Step Index | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ann vol % | 5.5 | 5.7 | 6.0 | 6.5 | 6.5 | 6.9 | 6.8 | **7.2** |

Up about 31% since inception, and at its all-time high now. Every other
instrument holds its volatility to within ~1% across seven to eight years
(Volatility 10: 10.1, 10.0, 10.0, 10.0, 10.2, 10.0, 9.9, 10.0).

Step is therefore the one instrument here where "what regime is this" is a
meaningful question. It is not an edge - a rising volatility parameter says
nothing about direction - but it is a real, dated, non-stationary fact.

---

---
[All findings](../README.md)
