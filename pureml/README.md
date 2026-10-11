# Pure ML Gold: can machine learning find an edge in XAUUSD?

**Author: Scott (ScottX Research)**

A from-scratch machine-learning study asking one question:

> **Can machine learning discover a repeatable, economically meaningful predictive structure in gold (XAUUSD), without being taught a human strategy?**

**Answer: no.** On a test split read exactly once, the final model's accuracy (51.2%) was below the market's own up-drift base rate (52.1%), and it lost money in both test years. The only statistically significant result in the whole study was *always long*, which is gold's 2023-24 rally, not skill. The full record is in [RESULTS.md](RESULTS.md).

A rigorous negative is a real result. The value of this folder is the **method**: a pipeline built so that it cannot fool itself, and that says "no" plainly when the answer is no.

## The rules the pipeline enforces

1. **No lookahead, ever.** Every feature is computable at its own timestamp. Scaling and imputation are fitted on training data only.
2. **The test split is untouched** until a single, pre-registered final evaluation.
3. **Baselines before models.** If ML cannot beat drift, always-long, always-short and a coin flip out of sample, say so.
4. **Accuracy is not the criterion.** Results are judged on cost-adjusted return, drawdown, turnover and stability across years, not hit rate.
5. **No parameter mining.** Every experiment goes in the ledger with its hypothesis and outcome, failures included.
6. **Let the data choose** the timeframe, target and horizon. They are research outputs, not assumptions.

## The pipeline, step by step

| Step | Script | What it does |
|---|---|---|
| R01 | `research/r01_data_audit.py` | Audits the raw M1/M5/M15 export: gaps, duplicates, spread, a 133-day hole. Fixes the date splits **once**: train / validation / test, by date. |
| R02 | `research/r02_target_research.py` | Chooses the target and horizon from the data: which timeframe and how far ahead has any information at all, after costs. |
| R03 | `research/r03_dataset.py` | Builds the dataset and **proves** it is leakage-safe: features recomputed with future bars appended must be bit-identical; no label crosses a split boundary (purging). |
| R04 | `research/r04_baselines.py` | Baselines first: drift, always long, always short, coin flip, simple momentum. The bar any model must clear. |
| R05 | `research/r05_models.py` | First model fits (L1/L2-regularised logistic regression, histogram gradient boosting) on train, judged on validation. |
| R06 | `research/r06_walkforward.py` | Expanding walk-forward: refit through time, so every prediction is made only with the past. |
| R07 | `research/r07_feature_information.py` | Model-free feature information: is there any signal in the features at all, and what is the ceiling? |
| R08 | `research/r08_horizon_sweep.py` | Timeframe × horizon sweep, with the multiple-testing burden recorded. |
| R09 | `research/r09_retest.py` | Re-tests the R08 survivors on data they were not selected on. |
| R10 | `research/r10_robustness.py` | Cost sensitivity, calibration and regime stability. |
| R11 | `research/r11_final_test.py` | The final test, **run once**, with parameters fixed before the script was written. |

Supporting modules:

| File | What it does |
|---|---|
| `config.py` | Paths, instrument, and the fixed split boundaries (never moved after seeing a result) |
| `data/loader.py` | Reads MT5 CSV exports; aggregates to higher timeframes on broker-aligned buckets |
| `data/features.py` | Backward-looking features only |
| `data/dataset.py` | Builds the dataset, purges labels at split boundaries, and verifies there is no lookahead |
| `models/fit.py` | Preprocessing fitted on train only; model specs; probability → position |
| `research/evaluate.py` | Cost-adjusted evaluation: net return, drift-adjusted accuracy, turnover, drawdown, t-statistics |

## Running it

Python 3.10+ with `numpy`, `pandas` and `scikit-learn`. You need your own MetaTrader 5 CSV exports of XAUUSD (market data is not redistributed here): `XAUUSD_M1.csv`, `XAUUSD_M5.csv`, `XAUUSD_M15.csv` with columns `time, open, high, low, close, tick_volume, spread` (spread in points).

```bash
pip install numpy pandas scikit-learn
PUREML_DATA=path/to/mt5_csvs python -m pureml.research.r01_data_audit
PUREML_DATA=path/to/mt5_csvs python -m pureml.research.r03_dataset     # leakage proof
# ... r04 to r10 in order; r11 only once, at the very end
```

Outputs are written to `artifacts/` (or `PUREML_ARTIFACTS`). If you use a different broker or period, review the split dates in `config.py` **before** running anything, and do not move them afterwards.

## Licence

MIT, see the [factory licence](../factory/LICENSE). Same terms, same author.
