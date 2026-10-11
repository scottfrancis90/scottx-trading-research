# Finding 12 - Engulfing candlestick pattern. Pre-registered, universe-wide. NEGATIVE.

The specification was given as a diagram and implemented exactly: body
engulfing, entry at the close of the second candle, stop at that candle's
low (buy) or high (sell), targets at 1:1, 1:2 and 1:3.

**Scope: 60 symbols x M30 and H1 x 3 RR x 4 trend lookbacks = 1,440 cells,
3,908,346 trades.** Six undefined quantities were pre-registered before the
run; the arbitrary ones were swept and every cell is reported.

### 12a - the result

**Edge over a stop-matched random entry:**

| | mean edge R/trade | cells positive |
|---|---:|---:|
| pessimistic | **+0.00013** | 717 / 1440 (49.8%) |
| optimistic | −0.01370 | 585 / 1440 (40.6%) |

**|t| > 2 in 70 of 1,440 cells, where chance expects 72.0.**

That is as clean a null as this study has produced. The pattern performs
identically to an arbitrary entry with the same risk geometry.

**Win rate against the geometric breakeven 1/(1+RR):**

| RR | breakeven | win (pess) | win (opt) |
|---|---:|---:|---:|
| 1:1 | 0.5000 | 0.4777 | 0.5015 |
| 1:2 | 0.3333 | 0.3268 | 0.3353 |
| 1:3 | 0.2500 | 0.2501 | 0.2546 |

The win rate brackets the rate a driftless random walk gives for free. Same
signature as the gold project's P23 (200 EMA + hammer), reached on a
different pattern, a different venue and 3.9 million trades.

**The trend filter contributes nothing.** Edge by lookback: L=0 −0.0031,
L=5 +0.0033, L=10 +0.0001, L=20 +0.0002 - while discarding 45% of the
signals (1,440,303 trades down to 786,642). "Appears after a downtrend" is
not doing work.

### 12b - cost, which decides it wherever cost exists

| kind | gross (pess..opt) | cost R | net (pess..opt) |
|---|---|---:|---|
| volatility | −0.013 .. +0.009 | 0.024 | −0.038 .. −0.016 |
| boom | −0.041 .. −0.024 | 0.017 | −0.059 .. −0.042 |
| gold | −0.022 .. +0.030 | **0.155** | −0.164 .. −0.112 |
| tactical | −0.045 .. +0.061 | **0.121** | −0.200 .. −0.094 |
| basket | −0.026 .. +0.032 | **0.622** | −0.649 .. −0.592 |
| equity | −0.067 .. +0.051 | **0.669** | −0.765 .. −0.647 |

Gross brackets zero everywhere. Net is negative everywhere the spread is
material. **Net is positive in both brackets in 237 of 1,440 cells (16.5%)**,
which is fewer than would be expected from noise around a zero-mean gross
given the cost spread across instruments.

### 12c - the internal contradiction that settles it

XAUUSD and XAUUSDmicro are **the same asset**, differing only in contract
size, so they must agree.

| symbol | trades | gross (pess) | net (pess) | edge vs control |
|---|---:|---:|---:|---:|
| XAUUSD | **7,260** | −0.042 .. +0.021 | **−0.19 .. −0.25** | +0.010 .. +0.064 |
| XAUUSDmicro | **426** | +0.061 .. +0.174 | **+0.01 .. +0.13** | +0.125 .. +0.169 |

They do not agree. The 426-trade sample says the pattern works and the
7,260-trade sample on the identical underlying says it does not. That is what
a small-sample false positive looks like, and it is present in this very
dataset as a worked example.

### 12d - two bugs in the test, both found and fixed before reporting

**The control was invalid.** The first control drew a random bar and set its
stop at that bar's own low. But an engulfing bar is BY CONSTRUCTION a large
bar, so its stop was roughly twice a random bar's (Volatility 75: 3,210
versus 1,248; gold: 2.84 versus 1.49). Smaller stops put both barriers inside
a single bar far more often - **control ambiguity 18-26% against the
pattern's 1-5%** - so the intrabar assumption dominated the control's result
and barely touched the pattern's. That produced a spurious **+0.159 R
"edge", positive in 96.2% of cells**. It measured stop size, not the pattern.
Replaced with a control that reuses the pattern's own stop distance,
price-rescaled, so only entry TIMING differs. Matched ambiguity: 0.0063
versus 0.0063.

**The spread lookup silently returned zero.** Symbol names were recovered
from the parquet slug, which replaces every non-alphanumeric character with
"_". Un-slugging gave "AAPL OQ" for "AAPL.OQ" and "Volatility 10  1s  Index"
for "Volatility 10 (1s) Index"; MT5 knows neither, `symbol_info` returned
None, and the spread stayed 0. Equities were reported at **zero cost** when
their true cost is **0.67 R**. Fixed by matching on the slug.

### 12e - the limit that no amount of care removes

Gross expectancy brackets zero at every RR, and the width of that bracket
comes entirely from the intrabar path problem (Finding 11f): OHLC cannot say
whether the stop or the target was touched first. Here the ambiguity rate is
low (0.6% median) because engulfing bars are large, so the bracket is tight
and the null is safe. But **no barrier strategy can be settled more precisely
than this on bar data**, and any test that reports a single number without
the bracket is hiding the assumption that produced it.

**Status: NEGATIVE. Well powered - 3.9 million trades, gross expectancy zero,
win rate on the geometric breakeven, no edge over a matched random entry, and
the trend filter adds nothing.**

---

---
[All findings](../README.md)
