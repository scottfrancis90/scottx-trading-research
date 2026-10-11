# Author: Scott (ScottX Research)
"""Strategy Factory -- configuration.

Every number here is a guard against the search fooling itself. The comments
say what each one is defending against.

ENVIRONMENT
    FACTORY_DATA     folder of CSV bars, one file per symbol and timeframe:
                     <SYMBOL>_<TF>.csv with columns time, open, high, low,
                     close, spread (spread in PRICE units). Default: ./data
    FACTORY_SYMBOLS  comma-separated symbols to search. Default: SYNTH1
    FACTORY_HOME     where runs, the ledger and holdout locks are written.
                     Default: ./factory_runs
"""
import os

# ---------------------------------------------------------------- paths
DATA_DIR = os.environ.get("FACTORY_DATA", "data")
HOME = os.environ.get("FACTORY_HOME", "factory_runs")
OUT = os.path.join(HOME, "runs")
LEDGER = os.path.join(HOME, "ledger.jsonl")
LOCKS = os.path.join(HOME, "locks")

# ---------------------------------------------------------------- timeframes
# The first one is the BASE: split boundaries are computed on it once, as
# dates, and applied to every timeframe, so no timeframe sees bars another
# timeframe cannot.
TIMEFRAMES = ("H1", "H4")
BARS_PER_DAY = {"M5": 288, "M15": 96, "M30": 48, "H1": 24, "H4": 6, "D1": 1}

# ---------------------------------------------------------------- splits
# TRAIN 50% | embargo | VALIDATE 25% | embargo | HOLDOUT 25%, by date, never
# shuffled. The embargo (calendar days) is longer than the longest trade the
# vocabulary can produce, so an open position cannot straddle a boundary.
TRAIN_FRAC = 0.50
VALID_FRAC = 0.25
EMBARGO_DAYS = 20

# ---------------------------------------------------------------- costs
# Slippage in R on every trade, on top of the spread taken from the data.
SLIP_R = 0.01

# A trade whose stop is narrower than this many spreads is refused. Without
# it, a search finds a dead stretch of the feed where ATR collapses to almost
# nothing, places a stop a tenth of the spread wide and books hundreds of R
# on one trade. No broker would accept that order either.
MIN_R_SPREADS = 8

# ---------------------------------------------------------------- GA
POPULATION = 200
GENERATIONS = 40
MAX_ACTIVE_GENES = 5
GENE_PENALTY_FROM = 3
# A low trade floor lets the GA find the smallest sample the rules permit,
# where a lucky mean survives. 400 trades on TRAIN is the hard floor.
MIN_TRADES = 400            # hard fail below this
SOFT_TRADES = 800           # fitness penalty below this

# ---------------------------------------------------------------- gates
PBO_MAX = 0.10
PLATEAU_MIN_POSITIVE = 0.80
CONTROL_MARGIN = 0.05       # candidate must beat its inverted control by this

os.makedirs(OUT, exist_ok=True)
os.makedirs(LOCKS, exist_ok=True)
