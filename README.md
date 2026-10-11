# ScottX Research: Forex, Gold & Deriv Synthetic Indices Backtests

**70+ trading strategy tests on Forex, Gold (XAUUSD) and Deriv synthetic indices, every one measured against a random-entry control, with the failures reported as plainly as the successes.**

Smart Money Concepts (ICT order blocks, fair value gaps, Candle Range Theory, liquidity sweeps), candlestick patterns, RSI / Bollinger / MACD rules, scalping, pyramiding, and a genetic-algorithm strategy factory. Tested on 28 forex pairs, gold and 79 Deriv synthetic indices (Boom, Crash, Volatility 75, Volatility 100, Jump, Step, Crash Boom Flip) with MetaTrader 5 data from 2017 to 2026.

> Most strategies in this repo **do not work**. That is the finding. If a rule you use is in here, you can see exactly how it was tested and why it failed.

---

## Highlights

- **A 90% win rate can still lose money.** Thirteen gold scalps won 90% of their trades in 2026 and every one lost money after the spread ([Finding 35](findings/035-is-there-a-90-win-scalp-on-gold-in-2026-yes-thirteen-of-them-all-lose-.md)). A fade that reached its target 85% of the time still lost on every trade on average ([Finding 60](findings/060-the-12-00-utc-fade-against-the-daily-bias-85-of-trades-reach-the-targe.md)). Win rate is not edge.
- **Deriv synthetic indices are fair games.** Boom, Crash and Volatility indices behave as martingales: no drift, no volatility clustering, no exploitable pattern ([Findings 1-10](findings/README.md#deriv-synthetic-indices-boom-crash-volatility-flip)).
- **ICT order blocks and FVGs, tested as written.** On H1 and H4 forex, a random zone does the same as an order block in most setups ([Findings 126-144](findings/README.md#smart-money-concepts-ict-order-blocks-fvg-crt-liquidity)).
- **Candle Range Theory (CRT)** setups are statistically indistinguishable from random entries ([Finding 67](findings/067-candle-range-theory-the-full-study-the-setups-are-statistically-indist.md)).
- **A genetic algorithm searched 62.7 million strategies on gold** and found nothing real. Twice it produced a "winner" that passed a holdout, and twice the winner turned out to be a lookahead bug ([Findings 74-86](findings/README.md#strategy-factory-genetic-algorithm-search-and-the-bugs-it-caught)). Those bugs, and how they were caught, are the most useful part of this repo for anyone building a backtester. [How the factory works](docs/STRATEGY_FACTORY.md), and [the code](factory/), runnable on synthetic data in four commands.
- **Forex pairs that move opposite each other**: a correlation study with a GA search for mirrored groups, checked on years the search never saw ([report](reports/opposite-forex-pairs/)).

- **Can machine learning predict gold?** A from-scratch ML study with a leak-proof pipeline, walk-forward validation and a test split read exactly once. The model lost to gold's own drift; the only significant result was "always long", which is the 2023-24 rally, not skill ([pureml](pureml/)).

## How every test is run

1. **The rule is written down before the test.** No tuning on the result.
2. **Random-entry control.** Every strategy is compared with random entries on the same instrument, same year, same direction and same stop and exit. On a trending market like gold, buying anything looks profitable; the control removes that drift.
3. **Both halves of the history.** 2017-2021 and 2022-2026 are reported separately. An edge that lives in one half is not an edge.
4. **Real costs.** The spread actually recorded at the time of each trade, not today's spread.
5. **No lookahead.** Higher-timeframe trades are replayed on lower-timeframe candles so a stop or a trailing move cannot be credited before price got there.
6. **Multiple testing is counted.** The more variants tried, the higher the bar.

More in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Repository

```
findings/                  one file per finding, indexed by topic in findings/README.md
findings/notes/            study scope, limitations, corrections and methods notes
reports/
  opposite-forex-pairs/    report (HTML, PDF, PNG), full pair table (CSV) and the script
docs/METHODOLOGY.md        how the tests are designed, and the mistakes that taught it
docs/STRATEGY_FACTORY.md   how the genetic-algorithm Strategy Factory works
factory/                   the Strategy Factory code: engine, GA, gates, holdout, example vocabulary
pureml/                    the machine-learning study on gold: leak-proof pipeline R01-R11 and its results
TOOLS.md                   the private indicators and EAs used alongside this research
```

## Data

MetaTrader 5 history from the Deriv broker: 28 forex pairs, XAUUSD and Deriv synthetic indices, M1 to D1, 2017-2026. Market data is not redistributed here; every finding names the instruments, timeframe and period so it can be reproduced.

## Tools

The research sits next to a set of private MT5 Expert Advisors and TradingView indicators. They are **not for sale** and are not published. See [TOOLS.md](TOOLS.md).

## Reach out

If anything here is worth discussing (a result, a method, a strategy you would like tested the same way), open a thread in [Discussions](../../discussions).

## Notes

- Research, not financial advice. Past results do not guarantee future results. Trading leveraged products can lose more than the deposit.

---

*Keywords: forex backtest, gold XAUUSD strategy, Deriv synthetic indices, Boom and Crash strategy, Volatility 75 index, ICT order block backtest, fair value gap, smart money concepts, Candle Range Theory, liquidity sweep, MT5 expert advisor, algorithmic trading research, genetic algorithm trading, random entry control, lookahead bias, quantitative trading.*
