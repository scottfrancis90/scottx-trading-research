# Author: Scott (ScottX Research)
"""R01 — data audit and objective timeframe selection.

Question: what does the gold data actually support?

This runs BEFORE any target, feature or model exists, because the timeframe
decision constrains everything downstream and must not be inherited from the
retired project (which assumed 1M).

Reported per candidate timeframe:
  * span, bar count, gaps
  * usable sample size after a chronological 60/20/20 split
  * transaction cost as a fraction of typical bar movement — the ratio that
    decides whether ANY edge at that timeframe is reachable
  * autocorrelation of returns at lag 1 — a first, assumption-free look at
    whether short-horizon structure exists at all

No model is fitted and no target is defined here.

Run:  python -m pureml.research.r01_data_audit
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import numpy as np

from ..config import ARTIFACT_DIR, SYMBOL, split_of
from ..data.loader import TF_MINUTES, aggregate, load_raw

CANDIDATES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]


def log(s):
    print(s, flush=True)


def gaps(bars):
    """Bar-to-bar time steps larger than one bar — sessions, weekends, holes."""
    step = np.diff(bars.time) / 60_000.0
    expected = bars.minutes
    big = step[step > expected * 1.5]
    return len(big), (float(np.max(step)) if len(step) else 0.0)


def main():
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r01_data_audit_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R01 — DATA AUDIT  (%s)" % SYMBOL)
    log("No target, no features, no model. Establishing what the data is.")
    log("")

    base = load_raw("M1")
    t0 = datetime.fromtimestamp(base.time[0] / 1000, tz=timezone.utc)
    t1 = datetime.fromtimestamp(base.time[-1] / 1000, tz=timezone.utc)
    log("source M1: %s bars   %s -> %s   (%.1f years)"
        % (f"{len(base):,}", t0.date(), t1.date(),
           (base.time[-1] - base.time[0]) / (365.25 * 86400_000)))
    ng, mx = gaps(base)
    log("           %s gaps > 1.5 bars, largest %.0f minutes (%.1f days)"
        % (f"{ng:,}", mx, mx / 1440.0))
    log("")

    log("%-5s %10s %9s %9s %9s %10s %11s %10s %9s"
        % ("TF", "bars", "train", "valid", "test", "med|ret|",
           "cost/|ret|", "spread", "AC(1)"))
    log("-" * 92)

    rows = {}
    for tf in CANDIDATES:
        b = base if tf == "M1" else aggregate(base, tf)
        ret = np.diff(np.log(b.close))
        absr = np.abs(ret)
        med_move = float(np.median(absr) * b.close[1:].mean())
        med_spread = float(np.median(b.spread))
        # round-trip cost relative to a typical bar's absolute movement
        cost_ratio = med_spread / med_move if med_move > 0 else np.inf
        ac1 = float(np.corrcoef(ret[:-1], ret[1:])[0, 1]) if len(ret) > 2 \
            else float("nan")
        counts = {"train": 0, "validation": 0, "test": 0}
        for t in b.time:
            counts[split_of(int(t))] += 1
        rows[tf] = {"bars": len(b), "splits": counts,
                    "median_abs_move_price": med_move,
                    "median_spread_price": med_spread,
                    "cost_over_move": cost_ratio, "autocorr_lag1": ac1}
        log("%-5s %10s %9s %9s %9s %10.4f %11.3f %10.3f %+9.4f"
            % (tf, f"{len(b):,}", f"{counts['train']:,}",
               f"{counts['validation']:,}", f"{counts['test']:,}",
               med_move, cost_ratio, med_spread, ac1))

    log("")
    log("READING THE COST COLUMN")
    log("  cost/|ret| is the median spread divided by the median absolute")
    log("  price move of one bar. Above ~1.0 the spread exceeds a typical")
    log("  bar's entire movement, and no per-bar signal can pay for itself.")
    log("")
    log("READING AC(1)")
    log("  Lag-1 autocorrelation of log returns. Near zero means no linear")
    log("  serial structure; strongly negative usually means bid-ask bounce")
    log("  rather than tradable mean reversion.")
    log("")

    viable = [tf for tf in CANDIDATES
              if rows[tf]["cost_over_move"] < 1.0
              and rows[tf]["splits"]["train"] >= 5000]
    log("Timeframes with cost < 1.0 x typical move AND >= 5,000 train bars:")
    log("  %s" % (", ".join(viable) if viable else "NONE"))

    with open(os.path.join(out_dir, "audit.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "generated": stamp,
                   "source_bars_m1": len(base),
                   "span": [str(t0), str(t1)],
                   "timeframes": rows, "viable": viable}, fh, indent=2)
    log("")
    log("written: %s" % os.path.join(out_dir, "audit.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
