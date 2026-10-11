# Author: Scott (ScottX Research)
"""Shared evaluation. Used identically by baselines and by models.

A position series `pos[t]` in [-1, +1] is held from bar t to bar t+1.

    pnl[t] = pos[t] * step[t]  -  |pos[t] - pos[t-1]| * spread[t] / 2

**Cost is charged on TURNOVER, not per bar.** Crossing the spread once costs
half of it, so a full round trip (0 -> +1 -> 0) costs exactly one spread. An
unchanged position costs nothing to hold.

This matters more than it sounds. Charging a spread every bar makes any
stable position look catastrophic — buy-and-hold gold rose $522/oz across
the training period yet scored -$6,753 under a per-bar charge. That is an
artifact of the accounting, not a property of the market.

Reported two ways:
  * ALL rows — every bar contributes
  * NON-OVERLAPPING rows — every k-th bar, for honest t-statistics, since
    adjacent rows share future bars

Directional accuracy is always printed beside the DRIFT base rate, never
beside 0.5, because gold trended strongly and a permanently-long model would
otherwise look skilful.
"""
from __future__ import annotations

import math
from typing import Dict

import numpy as np

__all__ = ["evaluate_positions", "format_row", "HEADER"]

HEADER = ("  %-22s %8s %7s %7s %10s %10s %8s %7s %7s %8s"
          % ("strategy", "bars", "acc", "drift", "net $", "$/bar",
             "t(ind)", "turn", "expo", "maxDD"))


def evaluate_positions(pos: np.ndarray, ds, mask: np.ndarray,
                       nonoverlap: np.ndarray,
                       cost_multiplier: float = 1.0) -> Dict:
    """Score a position series. `pos` is aligned to `ds`, values in [-1, 1]."""
    p = np.where(np.isfinite(pos), pos, 0.0)
    prev = np.concatenate(([0.0], p[:-1]))
    turn = np.abs(p - prev)

    step = np.where(np.isfinite(ds.step), ds.step, 0.0)
    earn = np.where(ds.contiguous, p * step, 0.0)     # no step across a gap
    cost = turn * ds.spread * 0.5 * cost_multiplier
    pnl = earn - cost

    m = mask
    n = int(m.sum())
    if n == 0:
        return {}
    pl = pnl[m]
    eq = np.cumsum(pl)
    dd = float(np.max(np.maximum.accumulate(np.concatenate(([0.0], eq)))
                      - np.concatenate(([0.0], eq))))
    win, loss = pl[pl > 0].sum(), -pl[pl < 0].sum()
    pf = float(win / loss) if loss > 0 else float("inf")

    on = np.abs(p[m]) > 1e-12
    exposure = float(on.mean())
    turnover = float(turn[m].mean())

    # directional accuracy of the SIGNAL against the horizon target
    sig = np.sign(p[m])
    live = sig != 0
    acc = (float(np.mean(sig[live] == np.sign(ds.y_ret[m][live])))
           if live.any() else float("nan"))
    drift = float(ds.y_up[m].mean())

    # honest t-statistic on non-overlapping bars
    mo = m & nonoverlap
    po = pnl[mo]
    t_ind = (float(po.mean() / (po.std(ddof=1) / math.sqrt(len(po))))
             if len(po) > 2 and po.std(ddof=1) > 0 else float("nan"))

    return {"n_bars": n, "accuracy": acc, "drift_base_rate": drift,
            "total_net": float(pl.sum()),
            "net_per_bar": float(pl.mean()),
            "gross_total": float(earn[m].sum()),
            "cost_total": float(cost[m].sum()),
            "t_independent": t_ind, "n_independent": int(mo.sum()),
            "turnover": turnover, "exposure": exposure,
            "profit_factor": pf, "max_drawdown": dd}


def format_row(name: str, r: Dict) -> str:
    if not r:
        return "  %-22s (no rows)" % name
    return ("  %-22s %8s %7.4f %7.4f %10.1f %10.4f %8.2f %7.3f %7.2f %8.1f"
            % (name, f"{r['n_bars']:,}", r["accuracy"], r["drift_base_rate"],
               r["total_net"], r["net_per_bar"], r["t_independent"],
               r["turnover"], r["exposure"], r["max_drawdown"]))
