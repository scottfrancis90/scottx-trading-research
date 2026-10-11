# Finding 13 - Hammer / shooting star and pin bar. Same protocol. NEGATIVE.

Single-bar rejection patterns, tested exactly as Finding 12: entry at the
close, stop at the wick extreme, targets 1:1/1:2/1:3, stop-matched random
control, intrabar bracket, trend-context sweep.

**Scope: 60 symbols x M30/H1 x 6 pattern variants x 3 trend lookbacks x 3 RR
= 6,375 cells, 10,901,304 trades.**

### 13a - the grid did not collapse this time

P23 in the gold project found its six hammer cells were algebraically two,
because "small body" plus "no opposite wick" already implies "long wick".
Checked explicitly here. With U fixed at 0.15, `body <= B` forces
`lower >= 1 - B - U`, i.e. >= 0.60 at B = 0.25 and >= 0.52 at B = 0.33. So
**W = 0.50 is inert and only W = 0.66 binds** - but the four hammer cells are
still distinct because B differs (98,888 / 92,249 / 149,621 / 111,525 trades
at H1). Both pin-bar cells bind (137,457 / 73,207). Reported so the sweep is
known to be narrower than it looks.

### 13b - the result

| | mean edge R/trade | cells positive |
|---|---:|---:|
| pessimistic | +0.00817 | 3328 / 6375 (52.2%) |
| optimistic | −0.01554 | 2673 / 6375 (41.9%) |

The bracket straddles zero. **Edge is positive in BOTH brackets in only 40.4%
of cells** - worse than a coin flip. |t| > 2 in 379 of 6,375 where chance
expects 318.8 (1.19x, on cells that are heavily non-independent).

Win rate against the geometric breakeven:

| RR | breakeven | win (pess) | win (opt) |
|---|---:|---:|---:|
| 1:1 | 0.5000 | 0.4892 | 0.5113 |
| 1:2 | 0.3333 | 0.3348 | 0.3415 |
| 1:3 | 0.2500 | 0.2536 | 0.2570 |

At 1:2 and 1:3 both ends sit marginally ABOVE breakeven - a gross tilt of
about +0.014 R at 1:3. **The median cost is 0.0298 R**, which is more than
twice the tilt. It does not survive.

### 13c - the mirror control settles it

Hammer and shooting star are traded symmetrically, so on a sign-flipped
instrument the bullish signals become bearish and the P&L should be
**identical**. A real effect therefore predicts an edge correlation near +1
between Boom N and Crash N.

**Measured across 540 matched pairs: correlation +0.0365.** Mean Boom edge
+0.00053, mean Crash edge −0.00753.

The effect does not replicate on the mirror. Whatever the 379 significant
cells are measuring, it is not a property of the pattern.

### 13d - cost, and internal consistency

| kind | gross (pess..opt) | cost R | net (pess..opt) |
|---|---|---:|---|
| volatility | −0.007 .. +0.004 | 0.030 | −0.039 .. −0.028 |
| boom | +0.018 .. +0.034 | 0.024 | −0.009 .. +0.006 |
| gold | −0.036 .. +0.010 | **0.197** | −0.213 .. −0.168 |
| tactical | −0.024 .. +0.077 | **0.170** | −0.230 .. −0.128 |
| basket | −0.072 .. −0.020 | **0.742** | −0.817 .. −0.764 |
| equity | −0.084 .. +0.055 | **0.949** | −1.088 .. −0.949 |

Unlike Finding 12, **XAUUSD and XAUUSDmicro agree this time** - all 24 cells
net negative on both (XAUUSD −0.226 to −0.289, micro −0.004 to −0.101). The
same-asset consistency check passes, and it passes on the negative side.

`flip` shows the largest edge (+0.081 in both brackets) but its instruments
are 45 days old, giving roughly 100 trades per cell, and Finding 9 already
established Flip is a martingale in both of its modes. Treated as noise.

The best cell of all 6,375, if cherry-picked, is Crash Boom Flip 1000 at
net +0.52 on **69 trades**.

### 13e - verdict

**NEGATIVE, and it replicates P23.** The gold project found a rejection
hammer's win rate pinned to the geometric breakeven on M1 XAUUSD with 16,353
trades. This finds the same thing on 60 instruments, two timeframes, a
different venue and 10.9 million trades, with a matched control that P23 did
not have. Three patterns now - engulfing, hammer, pin bar - all land on the
same number, which is the number a driftless random walk provides for free.

---

---
[All findings](../README.md)
