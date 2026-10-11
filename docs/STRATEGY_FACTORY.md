# The Strategy Factory: how it works

A genetic algorithm that searches for trading strategies on gold and forex, wrapped in gates designed so that **the search cannot fool itself**.

A genetic algorithm over indicators, timeframes and pairs is the purest overfitting machine there is. Evaluate 10,000 random strategies and hundreds will look significant by chance. So the factory is not "a GA plus a validation step at the end". It is a search engine where **the size of the search is charged against every result**, and the final test is a split the search can never see.

Results: [Findings 74-86 and 136-137](../findings/README.md#strategy-factory-genetic-algorithm-search-and-the-bugs-it-caught). Across all runs, more than 62 million strategies were evaluated and **no real survivor was found**. Two apparent survivors were traced to lookahead bugs. That is the design working.

---

## 1. Data: three splits, one direction

```
time ──▶  TRAIN 50%  ▒embargo▒  VALIDATE 25%  ▒embargo▒  HOLDOUT 25%
          GA fitness            survivor selection,       ONE test, ONE
          only                  corrected for ALL         pre-registered
                                strategies ever tried     prediction, then
                                                          the split is spent
```

- Split by date, never shuffled.
- A 20-day embargo between splits, longer than the longest trade, so an open position cannot leak across a boundary.
- The holdout is protected by a lock file. It runs once per strategy family, and the result is written whether it passes or fails.

## 2. Genome: what a strategy is made of

Each strategy (genome) is a small set of building blocks (genes):

```
market    instruments and timeframe
context   when the setup is allowed (e.g. a session, a volatility regime)
trigger   what fires the entry
filter    what blocks an entry
stop      where the stop goes
target    how the trade exits
```

- **Coarse grids only.** Parameters come from short lists (ATR 1 / 1.5 / 2 / 3, lookback 20 / 40 / 100). No "period = 37" that fits one history.
- **At most 5 active genes**, and each gene past the third costs fitness, so simpler rules win ties.
- **Mechanism tags.** Every gene declares why it could work (session, volatility expansion, mean reversion, trend, structure). Invalid combinations are refused at generation time; for example, a session gene on a synthetic index, because synthetic indices have no sessions.

## 3. One simulation engine

The GA, the controls, validation and the holdout all use the same engine:

- Gap-honest fills: a stop that price gaps through fills at the open, not at the stop.
- A candle that touches both the stop and the target counts as the **stop**.
- The spread recorded in the data at the time of the trade, plus measured slippage.
- Overlapping pending orders fill in **time order** (a bug that once filled them in signal order is documented in Finding 83).
- Before anything was built on it, the engine had to reproduce earlier hand-tested results trade for trade.

## 4. Fitness: computed on TRAIN only

```
fitness = mean R per trade
        - penalty for genes beyond 3
        - penalty below 800 trades        (hard fail below 400)
        - penalty if either half of TRAIN is negative
        - penalty for sitting on a peak
```

The GA maximises whatever it is given, including what you did not mean. Plain mean R finds the single luckiest cell on a hundred trades. The **peak penalty** handles that: each numeric gene is nudged one grid step each way, and if fewer than 80% of those neighbours are profitable the genome is sitting on a spike that will not generalise. Plateaus generalise; peaks do not.

The search itself is deliberately plain: population 200, tournament selection, crossover at gene boundaries, mutation of one grid step, a few elites kept. The bottleneck is not finding a maximum. Most maxima are noise, so the effort goes into the gates.

## 5. The ledger: the denominator

Every distinct strategy ever evaluated is appended to an append-only ledger, across all runs. This is the number the multiple-testing correction divides by. A second run on the same data does not get a fresh significance level: the burden is cumulative. With 10,000 strategies tried, Bonferroni requires |t| ≥ 4.6 on validation.

## 6. The validation gates: all of them, or dead

| Gate | Requirement |
|---|---|
| Enough trades | on the validation split itself |
| Both halves | mean R > 0 in each half of validation |
| Corrected significance | Bonferroni over the whole ledger |
| Inverted control | the same trades taken the other way must lose, by a margin |
| Shuffled control | the same entry times with random direction must come out at about minus the cost; if not, the geometry of the stop and target is doing the work, not the rule |
| Window-shift control | for session rules, shifting the window must make it worse |
| Plateau | at least 80% of neighbours profitable on validation too |
| Cross-section | on forex, a real edge works on most pairs; noise works on one or two |

Expect zero survivors on most runs.

## 7. The holdout: human first, machine once

A survivor is not tested on the holdout until a person can explain **why** it should work. "The GA found it" is not an answer. Then the prediction is written down with a numeric range and hashed, the holdout runs once, and the lock is written.

## 8. What it caught

The most valuable output of the factory was not a strategy. It was the bugs:

- **A survivor that passed a pre-registered holdout** and was still fake. The signal generator selected which bars to trade using information from the future. Every control passed, because the controls reused the same selection ([Finding 77](../findings/077-the-ga-survivor-was-lookahead-in-the-signal-generator-findings-75-and-.md)). Lesson: **controls cannot catch a selection bug**; only an independent re-implementation can.
- **Pending orders filling in signal order instead of time order** ([Finding 83](../findings/083-defect-12-overlapping-pending-orders-were-filling-in-signal-order-not-.md)).
- **A search collapse** that the collapse detector did not flag ([Finding 81](../findings/081-the-molecules-run-no-survivors-and-a-total-collapse-the-detector-did-n.md)).
- **A gene doing nothing at all**: every value gave identical results ([Finding 82](../findings/082-the-molecules-only-run-no-survivors-and-the-context-gene-was-doing-not.md)).

Each one is written up with how it was found, so the same mistakes are easier to spot in other backtesters.
