# Author: Scott (ScottX Research)
"""Bars, split three ways, in one direction only.

The split is computed ONCE from the base timeframe and expressed as DATES,
then applied to every timeframe. Computing it per timeframe would put the
boundaries in slightly different places and let a genome on one timeframe see
a few bars that a genome on another could not -- a small leak, but the kind
that is impossible to notice later.

Nothing here shuffles, resamples across a boundary, or returns the holdout
unless it is asked for by name.
"""
import os

import numpy as np
import pandas as pd

from factory import market as MK
from factory.config import DATA_DIR, EMBARGO_DAYS, TIMEFRAMES, TRAIN_FRAC, VALID_FRAC

_CACHE = {}


def load(tf, sym=None):
    """the raw series for one timeframe, validated, oldest first"""
    sym = sym or MK.symbols()[0]
    key = (tf, sym)
    if key in _CACHE:
        return _CACHE[key]
    if tf not in TIMEFRAMES:
        raise ValueError("timeframe %s is not in %s" % (tf, TIMEFRAMES))
    path = os.path.join(DATA_DIR, "%s_%s.csv" % (sym, tf))
    if not os.path.exists(path):
        raise FileNotFoundError("%s not found -- run `python -m factory.make_data` first, "
                                "or point FACTORY_DATA at your own CSV bars" % path)
    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").drop_duplicates("time").reset_index(drop=True)
    for c in ("open", "high", "low", "close"):
        df[c] = df[c].astype(float)
    if "spread" not in df.columns:
        df["spread"] = np.nan
    bad = (~np.isfinite(df[["open", "high", "low", "close"]].to_numpy())).any(axis=1)
    bad |= (df["high"] < df["low"]).to_numpy()
    if bad.any():
        df = df[~bad].reset_index(drop=True)
    _CACHE[key] = df
    return df


def boundaries(sym=None):
    """(train_end, valid_start, valid_end, holdout_start) as timestamps.

    Taken from the base timeframe and reused for every timeframe. Embargo gaps
    sit on both sides of the validation split, so no trade opened before a
    boundary can still be open after it.
    """
    t = load(TIMEFRAMES[0], sym)["time"]
    n = len(t)
    emb = pd.Timedelta(days=EMBARGO_DAYS)
    train_end = t.iloc[int(n * TRAIN_FRAC)]
    valid_end = t.iloc[int(n * (TRAIN_FRAC + VALID_FRAC))]
    return train_end, train_end + emb, valid_end, valid_end + emb


def _mask(t, which, sym):
    tr_end, va_start, va_end, ho_start = boundaries(sym)
    if which == "train":
        return t <= tr_end
    if which == "validate":
        return (t >= va_start) & (t <= va_end)
    if which == "holdout":
        return t >= ho_start
    raise ValueError("which must be train, validate or holdout -- got %r" % which)


def split(tf, which, sym=None):
    """one slice. Asking for the holdout is deliberately explicit -- there is
    no 'all' and no default that could hand it over by accident."""
    df = load(tf, sym)
    return df[_mask(df["time"], which, sym)].reset_index(drop=True)


def index_range(tf, which, sym=None):
    """(i0, i1) into the FULL series for this split.

    Indicators are computed on the whole series and then indexed, never
    recomputed on a slice. A rolling statistic truncated at a split boundary
    gives the SAME BAR a different value depending on which split it is in,
    which makes any comparison between train and validation meaningless.
    Nothing about this looks forward: every indicator is backward-looking.
    A trade is still forbidden from running past i1.
    """
    df = load(tf, sym)
    idx = np.flatnonzero(_mask(df["time"], which, sym).to_numpy())
    if not len(idx):
        return 0, 0
    return int(idx[0]), int(idx[-1]) + 1


def spread_price(tf, which="train", sym=None):
    """the median spread in PRICE, measured on the requested slice only.

    Measured on TRAIN by default: a cost taken from the holdout would be a
    small piece of holdout information leaking into the search.
    """
    s = split(tf, which, sym)["spread"].to_numpy(float)
    s = s[np.isfinite(s) & (s > 0)]
    return float(np.median(s)) if len(s) else 0.0


def describe():
    for sym in MK.symbols():
        tr_end, va_start, va_end, ho_start = boundaries(sym)
        print("%s" % sym)
        print("  TRAIN     ...          -> %s" % tr_end.date())
        print("  VALIDATE  %s -> %s" % (va_start.date(), va_end.date()))
        print("  HOLDOUT   %s -> ...     (untouched until one pre-registered test)" % ho_start.date())
        for tf in TIMEFRAMES:
            print("    %-3s %8d bars, median spread %.5f" % (tf, len(load(tf, sym)), spread_price(tf, sym=sym)))


if __name__ == "__main__":
    describe()
