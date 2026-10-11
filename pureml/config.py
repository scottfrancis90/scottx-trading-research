# Author: Scott (ScottX Research)
"""PURE ML GOLD — paths, instrument, and split boundaries.

Deliberately small. Nothing here encodes a trading idea; anything that looks
like a strategy parameter does not belong in this file.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

__all__ = ["ROOT", "RAW_DIR", "ARTIFACT_DIR", "SYMBOL", "SOURCE_TIMEFRAMES",
           "POINT_SIZE", "CONTRACT_SIZE", "ms", "TRAIN_END", "VALID_END",
           "SPLIT_TRAIN", "SPLIT_VALID", "SPLIT_TEST", "SPLIT_HOLDOUT",
           "HOLDOUT_START", "split_of"]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: MT5 CSV exports (XAUUSD_M1.csv, XAUUSD_M5.csv, XAUUSD_M15.csv). Set
#: PUREML_DATA to point elsewhere.
RAW_DIR = os.environ.get("PUREML_DATA", os.path.join(ROOT, "data", "raw"))
ARTIFACT_DIR = os.environ.get("PUREML_ARTIFACTS", os.path.join(ROOT, "artifacts"))

SYMBOL = "XAUUSD"
SOURCE_TIMEFRAMES = ("M1", "M5", "M15")

#: One point of XAUUSD price. The MT5 export reports spread in points.
POINT_SIZE = 0.01
#: Ounces per standard lot, for translating R into currency when needed.
CONTRACT_SIZE = 100.0


def ms(y: int, m: int, d: int) -> int:
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


SPLIT_TRAIN, SPLIT_VALID, SPLIT_TEST = "train", "validation", "test"
SPLIT_HOLDOUT = "holdout"

#: The source has a 133.4-day hole (2016-06-24 -> 2016-11-04) measured in
#: R01. Usable history therefore starts after it, so that no rolling window
#: ever spans the discontinuity. This is a data-quality boundary, not a
#: strategy choice.
DATA_START = ms(2016, 11, 5)

#: Chronological 60/20/20, placed at the 60th and 80th percentiles of the
#: post-hole M1 bar count (R01: 60.3% and 80.8% at these month starts) and
#: rounded to month boundaries. Fixed once. **Never moved to improve a
#: result** — moving a split boundary after seeing an outcome is the most
#: direct way to fabricate one.
TRAIN_END = ms(2021, 8, 1)
VALID_END = ms(2023, 3, 1)

#: The original CSV export ends 2024-08-23 and the `test` split above was
#: read once, in R11, and is spent. Data pulled live from MT5 on 2026-08-28
#: extends the history by two years. That new period has never been examined
#: by any experiment, so it is a genuine holdout — the clean out-of-sample
#: sample the project has lacked since R11.
#:
#: The boundary is the end of the old export, not a chosen date. Everything
#: before it keeps exactly the split it always had, so no previous result is
#: disturbed.
HOLDOUT_START = ms(2024, 8, 24)


def split_of(t_ms: int) -> str:
    """Which split a timestamp belongs to. Purely chronological.

    Returns ``None`` for anything before `DATA_START`, which belongs to no
    split and must never be used.
    """
    if t_ms < DATA_START:
        return None
    if t_ms < TRAIN_END:
        return SPLIT_TRAIN
    if t_ms < VALID_END:
        return SPLIT_VALID
    if t_ms < HOLDOUT_START:
        return SPLIT_TEST
    return SPLIT_HOLDOUT
