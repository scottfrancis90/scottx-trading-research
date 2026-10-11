# Finding 10 - the Gold RSI Tactical indices: levered gold, and an alpha that was a modelling artifact

Deriv publishes a matrix of Tactical Indices: {Gold, EURUSD, GBPUSD, BTCUSD,
ETHUSD, Silver, ...} x {RSI, BB, MACD, MACO} x {Pullback, Rebound, Trend Up,
Trend Down, Standard}. Gold has thirteen. This studies the four RSI ones.
`Gold RSI Trend Up Index` was not in Market Watch and was added, because the
study rule forbids analysing one half of a mirror pair.

History for all four is identical: **2024-12-06 to 2026-08-28**, 443 daily
bars, 1.7 years.

### 10a - four tickers, two series, and they are levered gold

| | r vs XAUUSD | beta |
|---|---:|---:|
| Trend Up | +0.518 | +1.203 |
| Pullback | −0.518 | −1.203 |
| Rebound | +0.733 | +1.902 |
| Trend Down | −0.733 | −1.902 |

Pullback = −Trend Up and Rebound = −Trend Down at **r = −0.9999**, and
log(TrendDown) + log(Rebound) has std 0.0067 across the whole life. They are
reciprocal pairs. **Four instruments, two independent series.**

### 10b - no lead, no lag

corr(index_t, gold_{t+k}) is **≤ 0.033 in absolute value at every k from −6
to +6**, against 0.52-0.73 at k = 0. They are computed from gold
contemporaneously, carry no early information about it, and receive none.

### 10c - five times the cost of gold for the same exposure

| | spread |
|---|---:|
| Gold RSI Rebound | 6.51 bp |
| Gold RSI Trend Up | 6.84 bp |
| Gold RSI Pullback | 7.27 bp |
| Gold RSI Trend Down | 7.65 bp |
| **XAUUSD** | **1.32 bp** |

Raw point spreads range 242 to 2,024, an 8x spread - but that is price level.
Normalised they are all ~7 bp. Swap is −10%/yr on all four, charged **both
long and short** (mode INTEREST_CURRENT).

The same 1.2x or 1.9x gold exposure is available by trading XAUUSD in larger
size at one fifth of the spread. **As a vehicle for gold exposure these are
strictly dominated.**

### 10d - the alpha, and why it was not real

Regressing index returns on gold returns produced a large, apparently
significant residual on the Rebound/Trend Down pair, consistent across every
timeframe and both years:

| | alpha | t |
|---|---:|---:|
| Trend Down M30 | +0.696 bp/bar | +2.53 |
| Trend Down H1 | +1.383 bp/bar | +2.53 |
| Trend Down D1 | **+39.03 bp/day** | **+3.71** |
| Trend Down 2025 | +18.54 bp/day | +1.49 |
| Trend Down 2026 | +65.72 bp/day | +3.33 |

All three timeframes agreed on 33-39 bp/day, sign was stable across both
years, and swap (−2.74 bp/day) was nowhere near large enough to offset it.
That implies roughly 9% per month, which was the tell.

**It is an artifact of fitting a linear model to a convex payoff.** A levered
or conditional strategy index is a nonlinear function of its underlying, of
the approximate form −beta*g + gamma*g^2. OLS on `g` alone cannot represent
the gamma term, so it lands in the intercept, and since E[g^2] > 0 always,
the intercept is pushed positive. The "alpha" was the convexity, misfiled.

Adding one term settles it:

| model | alpha | t |
|---|---:|---:|
| A. intercept + g | +39.03 bp/day | **+3.71** |
| B. separate beta on up/down gold days | −68.24 | −5.32 |
| C. intercept + g + \|g\| | −68.24 | −5.32 |
| **D. intercept + g + g^2** | **+5.47** | **+0.54** |

With the quadratic term present the alpha is **+5.47 bp/day at t = 0.54** -
nothing. The g^2 coefficient is +13.1 at **t = +10.04**, and the |g|
coefficient in model C is +0.984 at **t = +11.93**. The nonlinearity is
overwhelming; the alpha is not there.

Confirming the misspecification directly: beta is **−0.691 on gold-up days
and −2.659 on gold-down days**, and the rolling 60-day beta ranges −1.06 to
−2.14 (std 0.242). A single constant beta describes neither regime. The
cumulative residual is also extremely concentrated - the ten largest days
carry +65.6 percentage points of return out of 443 days.

### 10e - what is actually true

The convexity is real: Trend Down gains from gold's **variance**, Rebound
loses from it, mechanically, because one is a levered product and the other
its reciprocal. That is not skill and not an edge - it is the arithmetic of
leverage, it is symmetric within the pair, and capturing it means paying 7 bp
of spread (5x gold) plus 10% a year of swap for the privilege.

**Negative. No tradable structure, and the one number that looked like an
edge was a modelling error caught before it was believed.**

---

---
[All findings](../README.md)
