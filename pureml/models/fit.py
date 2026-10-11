# Author: Scott (ScottX Research)
"""Model fitting. Everything fitted here sees TRAIN ROWS ONLY.

Preprocessing (median imputation, standardisation) is fitted on train and
applied unchanged to validation. Fitting a scaler on all rows is a subtle,
extremely common leak: the validation mean leaks backwards into training.

Two model families, in deliberate order of complexity:

  logistic   L2- and L1-regularised linear. If a linear model cannot find
             anything, a tree ensemble finding something is more likely to
             be overfitting than insight.
  hgb        Histogram gradient boosting — non-linear, interaction-aware.

The label is direction over the horizon. Probabilities are turned into
positions by `positions_from_proba` below, which is where the trading
decision actually lives.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

__all__ = ["Preprocessor", "MODEL_GRID", "build_model",
           "positions_from_proba", "POSITION_GRID"]


@dataclass
class Preprocessor:
    """Median-impute then standardise. Statistics come from train only."""
    median: np.ndarray
    mean: np.ndarray
    scale: np.ndarray

    @classmethod
    def fit(cls, X: np.ndarray) -> "Preprocessor":
        med = np.nanmedian(X, axis=0)
        med = np.where(np.isfinite(med), med, 0.0)
        Z = np.where(np.isnan(X), med, X)
        mu = Z.mean(axis=0)
        sd = Z.std(axis=0)
        sd = np.where(sd > 1e-12, sd, 1.0)
        return cls(median=med, mean=mu, scale=sd)

    def transform(self, X: np.ndarray) -> np.ndarray:
        Z = np.where(np.isnan(X), self.median, X)
        Z = np.clip(Z, -1e12, 1e12)
        return (Z - self.mean) / self.scale


#: Pre-registered model grid. Fixed BEFORE any validation score is seen.
#: Every entry is reported, not just the best one.
MODEL_GRID: List[Tuple[str, Dict]] = [
    ("logit_l2_C0.01", {"kind": "logit", "penalty": "l2", "C": 0.01}),
    ("logit_l2_C0.1", {"kind": "logit", "penalty": "l2", "C": 0.1}),
    ("logit_l2_C1", {"kind": "logit", "penalty": "l2", "C": 1.0}),
    ("logit_l1_C0.01", {"kind": "logit", "penalty": "l1", "C": 0.01}),
    ("logit_l1_C0.1", {"kind": "logit", "penalty": "l1", "C": 0.1}),
    ("hgb_d2_lr0.03", {"kind": "hgb", "max_depth": 2, "lr": 0.03}),
    ("hgb_d2_lr0.1", {"kind": "hgb", "max_depth": 2, "lr": 0.1}),
    ("hgb_d3_lr0.03", {"kind": "hgb", "max_depth": 3, "lr": 0.03}),
    ("hgb_d3_lr0.1", {"kind": "hgb", "max_depth": 3, "lr": 0.1}),
]

#: Pre-registered position rules applied to every model's probabilities.
#: deadband — how far from 0.5 the probability must be to take a position
#: hold    — 1 means act on the current bar only; h means run an overlapping
#:           book of h trades at 1/h size each, which is the natural way to
#:           trade an h-bar forecast and caps turnover at 2/h
POSITION_GRID: List[Tuple[str, Dict]] = [
    ("d0.00_inst", {"deadband": 0.00, "hold": 1}),
    ("d0.01_inst", {"deadband": 0.01, "hold": 1}),
    ("d0.02_inst", {"deadband": 0.02, "hold": 1}),
    ("d0.00_hold", {"deadband": 0.00, "hold": 8}),
    ("d0.01_hold", {"deadband": 0.01, "hold": 8}),
    ("d0.02_hold", {"deadband": 0.02, "hold": 8}),
]


def build_model(spec: Dict, seed: int):
    if spec["kind"] == "logit":
        l1 = 1.0 if spec["penalty"] == "l1" else 0.0
        return LogisticRegression(
            l1_ratio=l1, C=spec["C"],
            solver="liblinear" if l1 == 1.0 else "lbfgs",
            max_iter=2000, random_state=seed)
    if spec["kind"] == "hgb":
        return HistGradientBoostingClassifier(
            max_depth=spec["max_depth"], learning_rate=spec["lr"],
            max_iter=300, min_samples_leaf=200, l2_regularization=1.0,
            early_stopping=False, random_state=seed)
    raise ValueError(spec["kind"])


def positions_from_proba(proba: np.ndarray, deadband: float,
                         hold: int) -> np.ndarray:
    """Turn P(up) into a position series in [-1, +1].

    With `hold` > 1 the position is the trailing mean of the last `hold`
    signals: an overlapping book of `hold` trades at 1/hold size each. This
    is not smoothing for its own sake — an h-bar forecast acted on every bar
    IS an overlapping book, and pretending otherwise charges h times the
    real cost.
    """
    s = np.zeros(len(proba))
    s[proba >= 0.5 + deadband] = 1.0
    s[proba <= 0.5 - deadband] = -1.0
    if hold <= 1:
        return s
    k = np.cumsum(np.concatenate(([0.0], s)))
    out = np.zeros(len(s))
    out[hold - 1:] = (k[hold:] - k[:-hold]) / hold
    for i in range(min(hold - 1, len(s))):      # partial book while filling
        out[i] = s[:i + 1].sum() / hold
    return out
