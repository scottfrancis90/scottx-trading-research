# Finding 92 - Boom/Crash replicates the null, and the outlier guard has a hole the size of the top 1%.

*2026-09-28, overnight pass, item 1. Boom/Crash M30, 10 instruments.
TRAIN + VALIDATE by date; last 25% not read.*

Replication of the Findings 90/91 retrace model on a third asset class. Stop-outs
priced at the calibrated **-1.143 R** spike fill, never -1.000 (that assumption
alone was worth +0.064 R a trade in Finding 88). Minimum R of 8 spreads enforced.

### Probability: the null replicates

| | TRAIN | VALIDATE |
|---|---|---|
| n | 12,260 | 5,782 |
| reached target | 13.1% | 12.9% |
| geometry says | 16.4% | 16.5% |
| **excess** | **-3.26 pp** (t -10.19) | **-3.67 pp** (t -7.92) |

Negative on both splits, significantly. Same answer as FX (Finding 90) and gold.
Three asset classes now agree: the method gets **fair odds at best**, and on
Boom/Crash slightly worse than fair.

### Expectancy looked positive. It was a tail.

The R expectancy read **+0.6292 R (t +6.61)** on TRAIN and +0.3423 (t +3.75) on
VALIDATE -- with probability NEGATIVE. That combination is only possible if a
few enormous winners carry the book, so the tail was checked:

| | TRAIN | VALIDATE |
|---|---|---|
| median trade | **-1.1643 R** | -1.1706 R |
| top 1% of trades, share of total profit | **123.1%** | **154.9%** |
| top 5% share | 222.8% | 330.8% |
| mean, top 1% trimmed | **-0.1471 R** | **-0.1897 R** |
| mean, top 5% trimmed | -0.8134 R | -0.8318 R |
| largest reward ratio dB/dS | 855 : 1 | 360 : 1 |

The typical trade is a full stop-out. Remove the best 1% and both splits lose.
This is a lottery-ticket book, not an edge.

### The guard that should have caught it, and did not

`fitness.outlier_dominated()` fails a genome when ONE trade carries more than
40% of the total. Here the single biggest trade is **5.9%** -- it passes
cleanly -- while the top 1% collectively carries 123%.

**The guard tests the wrong statistic.** A book can be entirely tail-driven
without any single trade dominating it. The check should be a trimmed mean, or
the share held by the top 1%, not the maximum.

This did not matter for the GA runs on gold and FX, where reward ratios are
bounded by an `r_multiple` or a capped structure target. It matters wherever
the target is an unbounded distance to the next level -- which is exactly what
the user's method uses.

**Recommendation: add a trimmed-mean check to `fitness.py`. A genome whose mean
flips sign when the top 1% of trades is removed is not a result.**

**Item 1 status: null replicated. Fourteenth measurement defect of the run.**

---

---
[All findings](../README.md)
