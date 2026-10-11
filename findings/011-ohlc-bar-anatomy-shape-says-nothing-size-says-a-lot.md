# Finding 11 - OHLC bar anatomy: shape says nothing, size says a lot

Groundwork for a future entry rule, run on 60 symbols x M30/H1 = 120 cells
(`artifacts/ohlc/ohlc.csv`, module `ohlc.py`).

### 11a - bar shape does not distinguish a real market from a random walk

Medians on H1, by instrument class:

| kind | body/range | upper wick | lower wick | close position | share with efficiency < 0.25 |
|---|---:|---:|---:|---:|---:|
| volatility (25) | 0.468 | 0.267 | 0.265 | 0.499 | 0.253 |
| boom (10) | 0.506 | 0.244 | 0.247 | 0.468 | 0.229 |
| flip (4) | 0.526 | 0.234 | 0.241 | 0.502 | 0.213 |
| step (1) | 0.467 | 0.266 | 0.267 | 0.498 | 0.254 |
| gold (3) | 0.440 | 0.272 | 0.285 | 0.518 | 0.276 |
| equity (2) | 0.453 | 0.274 | 0.273 | 0.504 | 0.274 |
| tactical (4) | 0.462 | 0.269 | 0.268 | 0.499 | 0.259 |

**A gold bar and a Volatility 75 bar are the same shape.** Body is 0.44-0.53
of range everywhere, wicks are a quarter each, the close sits mid-range, and
**21-28% of bars have efficiency below 0.25 in every instrument**, including
instruments proven to be memoryless random walks.

This is the direct answer to "filter out the noise bars". A wide-range bar
with a small body is not an anomaly and not a warning sign - **it is the
ordinary output of any price process at all**, and it occurs at the same rate
in a series that provably contains no information. **No shape-based filter
can separate signal bars from noise bars, because the shape distribution is
the same either way.**

### 11b - direction is not predictable from bar shape

Sorting bars into quintiles on close-position, efficiency or body, and
measuring the next bar's return:

| feature | cells | \|t\| > 2 | chance | max \|t\| |
|---|---:|---:|---:|---:|
| close position (M30) | 60 | 8 | 3.0 | 5.50 (XAUEUR) |
| close position (H1) | 60 | 5 | 3.0 | 4.81 (XAUEUR) |
| efficiency (M30) | 60 | 3 | 3.0 | 2.73 |
| efficiency (H1) | 60 | 4 | 3.0 | 2.30 |

Only close-position clears chance, only on the gold complex, and only as
**mean reversion** - a bar closing near its high is followed by a lower bar.
That is the bid-ask bounce again (closing on the high means closing at the
ask), and the economics settle it:

| | spread of the effect | cost to trade it |
|---|---:|---:|
| XAUUSD | **0.457 bp** | **1.32 bp** |
| XAUEUR | 0.870 bp | - |

**The effect is about a third of the spread it would have to pay.** Real,
measurable, and not worth crossing the bid-ask for. Same conclusion as
Finding 7, reached from bar shape rather than from returns.

### 11c - measurement error found and corrected

Range autocorrelation was first computed on ABSOLUTE range. Absolute range
tracks the price level, and price level is highly persistent, so the measure
is inflated for any instrument whose price wanders far. Corrected to
range/close:

| kind | absolute (wrong) | relative (correct) |
|---|---:|---:|
| volatility | **0.248** | **−0.000** |
| boom | 0.041 | 0.001 |
| crash | 0.060 | −0.002 |
| flip | 0.049 | 0.014 |
| step | 0.005 | 0.074 |
| gold | 0.734 | 0.606 |
| tactical | 0.663 | 0.604 |
| equity | 0.427 | 0.429 |
| basket | 0.737 | 0.618 |

The apparent range persistence in the Volatility indices was **entirely** the
price-level artifact and would have contradicted Finding 1. The real
instruments barely move, because theirs was real.

### 11d - size IS strongly predictable, and only on real instruments

Relative-range autocorrelation, corrected:

| | lag 1 | lag 10 | lag 50 |
|---|---:|---:|---:|
| XAUUSD | 0.569 | 0.234 | 0.238 |
| XAUEUR | 0.626 | 0.333 | 0.286 |
| Gold Basket | 0.618 | 0.348 | 0.276 |
| Gold RSI Trend Down | 0.641 | 0.337 | 0.193 |
| AAPL / MSFT | 0.429 | −0.13 | 0.04 |
| **all synthetics** | **≈ 0.00** | **≈ 0.00** | **≈ 0.00** |

Gold's range is still correlated with itself **fifty hours later**. And in
practical terms: after a top-quintile range bar, gold's next bar is about
**6x wider** than after a bottom-quintile bar (ratio 6.03; Gold Basket 7.26,
equities 3.4).

**So: direction is unpredictable, size is very predictable - on real
instruments only.** A stop or position size derived from recent range is
justified on gold and the equities and is meaningless on a synthetic, where
recent range says nothing about the next range.

### 11e - the excursion floor, which is the number a bot actually needs

Entering long at any close, over the next 10 bars, measured in units of the
entry bar's own range:

| kind | median MFE | median MAE | ratio | P(MAE > 1 range) |
|---|---:|---:|---:|---:|
| volatility | 1.382 | 1.374 | 1.007 | 0.620 |
| boom | 1.446 | 1.511 | 0.953 | 0.653 |
| flip | 1.347 | 1.645 | 0.884 | 0.678 |
| gold | 1.468 | 1.415 | 1.031 | 0.614 |
| equity | 1.605 | 1.650 | 0.974 | 0.654 |
| tactical | 1.580 | 1.554 | 1.018 | 0.639 |

Favourable and adverse excursion are **the same size** in every instrument
(ratio 0.88-1.06). And **a stop one entry-bar-range away is breached 61-68%
of the time within ten bars, everywhere.** That is the noise floor a bot has
to clear, and it does not vary by instrument, class, or timeframe.

### 11f - the limit of OHLC, stated plainly

OHLC gives four numbers and no ordering. For any bar that is not a marubozu
you cannot tell whether the high came before the low. So **OHLC alone can
never answer "would my stop have been hit before my target"** - the single
question that decides every barrier or stop-based rule. The MFE/MAE figures
above are upper bounds on what is knowable, not the answer. Settling it needs
tick data, and it is the same assumption the gold project's barrier labelling
(P13/P21) rested on rather than observed.

---

---
[All findings](../README.md)
