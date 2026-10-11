# Author: Scott (ScottX Research)
"""R08 — does the null hold across timeframes and horizons?

R03-R07 all test one cell: H1 with an 8-hour horizon, chosen in R02 on
economic grounds. Concluding "Pure ML failed" from one cell would overstate
the result — the honest version is either "it failed everywhere we looked" or
"it failed here but not there", and only a sweep can tell them apart.

This is ONE experiment, not sixteen. The grid is pre-registered below, every
cell is reported, and the multiple-testing cost is stated. It is explicitly
NOT a search for a cell that works: no cell graduates on the strength of this
sweep alone. If a cell looks alive it goes back through R05's rotation null
and R06's walk-forward before anything is claimed.

Fixed for every cell, so nothing is tuned per-cell:
  models   logit_l2_C0.1 (linear) and hgb_d2_lr0.03 (non-linear)
  rule     overlapping book of `horizon` trades, no deadband
  compare  always_long on the identical bars

Train -> validation. The test split is not read.

Run:  python -m pureml.research.r08_horizon_sweep
"""
from __future__ import annotations

import json
import os
import time
import warnings
from datetime import datetime, timezone

import numpy as np

from ..config import (ARTIFACT_DIR, DATA_START, SPLIT_TRAIN, SPLIT_VALID,
                      SYMBOL)
from ..data.dataset import build_dataset, nonoverlap_mask
from ..data.loader import aggregate, load_raw
from ..models.fit import Preprocessor, build_model, positions_from_proba
from .evaluate import evaluate_positions

TIMEFRAMES = ("M15", "M30", "H1", "H4")
HORIZONS = (1, 4, 8, 16)
MODELS = [("logit_l2_C0.1", {"kind": "logit", "penalty": "l2", "C": 0.1}),
          ("hgb_d2_lr0.03", {"kind": "hgb", "max_depth": 2, "lr": 0.03})]
SEED = 20260828

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def log(s):
    print(s, flush=True)


def main():
    t0 = time.time()
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r08_sweep_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R08 — TIMEFRAME x HORIZON SWEEP  (%s)" % SYMBOL)
    log("%d timeframes x %d horizons x %d models = %d cells, all reported."
        % (len(TIMEFRAMES), len(HORIZONS), len(MODELS),
           len(TIMEFRAMES) * len(HORIZONS) * len(MODELS)))
    log("Train -> validation. Test not read.")
    log("")

    base = load_raw("M1").slice_from(DATA_START)
    results = []

    log("  %-5s %-4s %-15s %9s %9s %9s %9s %7s %7s %9s"
        % ("tf", "k", "model", "train net", "val gross", "val cost",
           "val net", "acc", "drift", "long net"))
    for tf in TIMEFRAMES:
        bars = base if tf == "M1" else aggregate(base, tf)
        for k in HORIZONS:
            ds = build_dataset(tf, k, bars=bars)
            nov = nonoverlap_mask(ds)
            mtr, mva = ds.mask(SPLIT_TRAIN), ds.mask(SPLIT_VALID)
            if mtr.sum() < 2000 or mva.sum() < 500:
                log("  %-5s %-4d  (too few rows: %d train / %d validation)"
                    % (tf, k, int(mtr.sum()), int(mva.sum())))
                continue
            pre = Preprocessor.fit(ds.X[mtr])
            Xall = pre.transform(ds.X)
            al = evaluate_positions(np.ones(len(ds)), ds, mva, nov)
            for mname, spec in MODELS:
                clf = build_model(spec, SEED)
                clf.fit(Xall[mtr], ds.y_up[mtr])
                pr = clf.predict_proba(Xall)[:, 1]
                pos = positions_from_proba(pr, deadband=0.0, hold=k)
                rt = evaluate_positions(pos, ds, mtr, nov)
                rv = evaluate_positions(pos, ds, mva, nov)
                results.append({
                    "timeframe": tf, "horizon": k, "model": mname,
                    "n_train": int(mtr.sum()), "n_valid": int(mva.sum()),
                    "train_net": rt["total_net"],
                    "valid_gross": rv["gross_total"],
                    "valid_cost": rv["cost_total"],
                    "valid_net": rv["total_net"],
                    "valid_acc": rv["accuracy"],
                    "valid_drift": rv["drift_base_rate"],
                    "valid_t": rv["t_independent"],
                    "turnover": rv["turnover"],
                    "always_long_net": al["total_net"]})
                r = results[-1]
                log("  %-5s %-4d %-15s %9.1f %9.1f %9.1f %9.1f %7.4f %7.4f "
                    "%9.1f"
                    % (tf, k, mname, r["train_net"], r["valid_gross"],
                       -r["valid_cost"], r["valid_net"], r["valid_acc"],
                       r["valid_drift"], r["always_long_net"]))
    log("")

    log("=" * 104)
    log("SUMMARY")
    log("=" * 104)
    v = np.array([r["valid_net"] for r in results])
    beat = [r for r in results if r["valid_net"] > max(0.0,
                                                       r["always_long_net"])]
    pos_cells = [r for r in results if r["valid_net"] > 0]
    log("  cells run                       %d" % len(results))
    log("  validation net > 0              %d" % len(pos_cells))
    log("  validation net > always_long    %d" % len(beat))
    log("  best cell                       %.1f   worst %.1f   median %.1f"
        % (v.max(), v.min(), float(np.median(v))))
    log("")
    if beat:
        log("  Cells that beat both zero and always_long:")
        for r in sorted(beat, key=lambda z: -z["valid_net"]):
            log("    %-5s k=%-3d %-15s net %+9.1f  gross %+9.1f  acc %.4f "
                "(drift %.4f)  t=%+.2f"
                % (r["timeframe"], r["horizon"], r["model"], r["valid_net"],
                   r["valid_gross"], r["valid_acc"], r["valid_drift"],
                   r["valid_t"]))
        log("")
        log("  With %d cells searched, roughly %.1f would clear zero by chance"
            % (len(results), 0.5 * len(results)))
        log("  alone. NOTHING above is a result yet. Any cell carried forward")
        log("  must pass R05's rotation null and R06's walk-forward first.")
    else:
        log("  NO CELL beats both zero and always_long anywhere in the grid.")
        log("  The negative result is not specific to H1 / 8 hours.")
    log("")

    with open(os.path.join(out_dir, "sweep.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "generated": stamp,
                   "timeframes": list(TIMEFRAMES), "horizons": list(HORIZONS),
                   "models": [m[0] for m in MODELS],
                   "n_cells": len(results), "results": results},
                  fh, indent=2, default=float)
    log("elapsed %.1fs   written: %s" % (time.time() - t0, out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
