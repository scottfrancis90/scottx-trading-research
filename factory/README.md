# Strategy Factory: code

**Author: Scott (ScottX Research)**

A genetic algorithm that searches for trading strategies, wrapped in gates designed so that the search cannot fool itself. The design and the reasoning behind it are in [docs/STRATEGY_FACTORY.md](../docs/STRATEGY_FACTORY.md). This page is how to run it and how the code fits together.

The vocabulary in `genome.py` is an **example** made of textbook ideas (Donchian channel, ATR channel, EMA cross, ATR stop, R target, trailing stop). Swap in your own genes; everything else works unchanged.

## Quick start

Needs Python 3.10+ with `numpy` and `pandas` (`pip install -r requirements.txt`). Run from the repository root.

```bash
# 1. make synthetic test data (pure noise)
python -m factory.make_data 1 10          # 1 symbol, 10 years of H1 and H4 bars

# 2. prove the engine is honest before trusting anything it says
python -m factory.test_engine

# 3. see the vocabulary
python -m factory.genome

# 4. search TRAIN, gate on VALIDATE, write a report
python -m factory.run 4 40 1              # generations, population, seed
```

On pure noise the factory **must** report zero survivors. Then try a market with a small real effect planted in it:

```bash
python -m factory.make_data 1 10 --edge   # momentum after a 40-bar breakout
python -m factory.run 4 40 1
```

On this machine the two runs gave:

| Data | Survivors | What survived |
|---|---|---|
| Pure random walk | **0** | nothing; every candidate failed at least one gate |
| Planted breakout effect | **2** | 20-bar breakout rules in the breakout direction, which is the planted mechanism |

Near-miss variants of the planted rule were still killed. For example, one failed the shuffled-direction control because its trade timing alone made money with a random direction.

### Your own data

One CSV per symbol and timeframe, `<SYMBOL>_<TF>.csv`, with columns `time, open, high, low, close, spread` (spread in price units).

```bash
FACTORY_DATA=path/to/csvs FACTORY_SYMBOLS=EURUSD,GBPUSD,USDJPY python -m factory.run 25 150 1
```

With several symbols the trades are pooled, and a survivor must also work on enough **independent** symbols. Correlated pairs are discounted using the eigenvalue spectrum of their return correlations.

## How it works, step by step

```
make_data / your CSVs
        │
   data.py ──── splits by DATE: TRAIN 50% │ embargo │ VALIDATE 25% │ embargo │ HOLDOUT 25%
        │
   genome.py ── what a strategy is: context, trigger, filter, stop, target, manage, timeframe, hold
        │
 evaluate.py ── genome → signals (complete at a bar's close, acted on from the next bar)
        │
 simulate.py ── signals → trades (gap-honest fills, stop wins ties, time-ordered fills, real spread)
        │
  fitness.py ── TRAIN only: lower confidence bound of mean R, penalties, plateau test; the LEDGER
        │
      ga.py ─── population, tournament, crossover at gene boundaries, one-step mutation
        │
 validate.py ── the gates on VALIDATE, all of them or dead
        │
  report.py ─── a page naming the gate that killed each candidate, plus spec.json for a survivor
        │
 holdout.py ─── one locked, pre-registered test per strategy family, ever
```

| File | What it does | The mistake it prevents |
|---|---|---|
| `config.py` | Splits, costs, GA size, trade floors, gate thresholds | A trade floor that is too low lets the GA find the smallest lucky sample |
| `data.py` | Loads bars, computes the three splits once, as dates | Different boundaries per timeframe leak bars between splits |
| `genome.py` | The vocabulary, mutation, crossover, neighbours, fingerprint, known families | A huge vocabulary finds more "winners", none of them real |
| `evaluate.py` | Turns a genome into orders | Acting on a bar before it closes |
| `simulate.py` | The one engine everything uses | Same-bar ambiguity resolved in the rule's favour; pending orders filled in signal order instead of time order |
| `fitness.py` | Fitness on TRAIN, the plateau test, the ledger | Rewarding a spike in the search surface; forgetting how many strategies were tried |
| `ga.py` | The search loop and the collapse warning | A search that folds onto one idea and calls it breadth |
| `validate.py` | The gates | Trusting a TRAIN winner |
| `holdout.py` | The final one-shot test | Running "just one more check" on the holdout |
| `test_engine.py` | Random entries must lose the cost; hand-worked trades | An engine that invents money |

## The gates

A candidate must pass **all** of these on the validation split:

1. **Enough trades** on validation itself.
2. **Both halves** of validation positive.
3. **Bonferroni** over every strategy ever evaluated: the ledger is cumulative across runs.
4. **Inverted control**: the same trades taken the other way must lose, by a margin.
5. **Shuffled control**: the same trades with a random direction must not make money. If they do, the timing or the stop/target geometry is doing the work, not the rule.
6. **Window shift** (session rules only): moving the time window must make it worse.
7. **Plateau**: most one-step neighbours must also be profitable.
8. **Collapse check**: a survivor that only reproduces a strategy you already know is not a discovery.

With several symbols, a ninth gate requires the rule to work on enough independent symbols.

## Outputs

`FACTORY_HOME` (default `./factory_runs`) receives:

- `ledger.jsonl`: every strategy ever evaluated, append-only. This is the denominator.
- `runs/<tag>.md`: the run report, with every candidate and the gate that killed it.
- `runs/<tag>_survivor<k>.json`: a survivor's rules, ready for an EA template.
- `locks/`: one file per strategy family whose holdout has been spent.

## Licence

MIT, see [LICENSE](LICENSE).
