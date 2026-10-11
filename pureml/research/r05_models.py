# Author: Scott (ScottX Research)
"""R05 — fit models and test them against the R04 baselines.

Everything is fitted on TRAIN and scored on VALIDATION. The test split is
not read, not loaded, not touched.

Guard against parameter mining
------------------------------
The grid (9 models x 6 position rules = 54 configurations) is pre-registered
in `pureml/models/fit.py` and **every one of the 54 is reported**, not just
the winner. Reporting only the best of 54 would be exactly the practice the
project brief forbids.

To make "best of 54" interpretable, the same 54-cell search is repeated on
ROTATED training labels: the label vector is circularly shifted by a large
random offset, which destroys any feature-label relationship while preserving
the labels' own autocorrelation and their drift. Whatever the best-of-54
achieves under rotation is what selection alone buys. The real result has to
beat that distribution, not zero.

Run:  python -m pureml.research.r05_models
"""
from __future__ import annotations

import json
import os
import time
import warnings
from datetime import datetime, timezone

import numpy as np

from ..config import ARTIFACT_DIR, SPLIT_TRAIN, SPLIT_VALID, SYMBOL
from ..data.dataset import build_dataset, nonoverlap_mask
from ..models.fit import (MODEL_GRID, POSITION_GRID, Preprocessor,
                          build_model, positions_from_proba)
from .evaluate import evaluate_positions

TIMEFRAME, HORIZON = "H1", 8
SEED = 20260828
N_NULL = 8


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def log(s):
    print(s, flush=True)


def fit_grid(Xtr, ytr, Xall, seed):
    """Fit every model in the grid on train; return P(up) over all rows."""
    out = {}
    for name, spec in MODEL_GRID:
        clf = build_model(spec, seed)
        clf.fit(Xtr, ytr)
        out[name] = clf.predict_proba(Xall)[:, 1]
    return out


def score_grid(probas, ds, nov):
    """Evaluate every (model, position rule) pair on train and validation."""
    mtr, mva = ds.mask(SPLIT_TRAIN), ds.mask(SPLIT_VALID)
    rows = []
    for mname in probas:
        for pname, pspec in POSITION_GRID:
            pos = positions_from_proba(probas[mname], **pspec)
            rt = evaluate_positions(pos, ds, mtr, nov)
            rv = evaluate_positions(pos, ds, mva, nov)
            rows.append({
                "model": mname, "rule": pname,
                "train_net": rt["total_net"], "valid_net": rv["total_net"],
                "valid_acc": rv["accuracy"], "valid_drift": rv["drift_base_rate"],
                "valid_t": rv["t_independent"], "turnover": rv["turnover"],
                "exposure": rv["exposure"],
                "valid_gross": rv["gross_total"],
                "valid_cost": rv["cost_total"],
                "mean_pos": float(np.mean(pos[mva])),
                "valid_dd": rv["max_drawdown"]})
    return rows


HDR = ("  %-16s %-12s %10s %10s %10s %9s %7s %7s %8s"
       % ("model", "rule", "train net", "val gross", "val cost", "val net",
          "acc", "turn", "mean pos"))


def fmt(r):
    return ("  %-16s %-12s %10.1f %10.1f %10.1f %9.1f %7.4f %7.3f %8.3f"
            % (r["model"], r["rule"], r["train_net"], r["valid_gross"],
               -r["valid_cost"], r["valid_net"], r["valid_acc"],
               r["turnover"], r["mean_pos"]))


def main():
    t_start = time.time()
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r05_models_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R05 — MODELS  (%s %s, horizon %d)" % (SYMBOL, TIMEFRAME, HORIZON))
    log("Fitted on train. Scored on validation. Test is not read.")
    log("Grid: %d models x %d position rules = %d configurations, all reported."
        % (len(MODEL_GRID), len(POSITION_GRID),
           len(MODEL_GRID) * len(POSITION_GRID)))
    log("")

    ds = build_dataset(TIMEFRAME, HORIZON)
    nov = nonoverlap_mask(ds)
    mtr, mva = ds.mask(SPLIT_TRAIN), ds.mask(SPLIT_VALID)

    pre = Preprocessor.fit(ds.X[mtr])          # train only
    Xall = pre.transform(ds.X)
    Xtr, ytr = Xall[mtr], ds.y_up[mtr]

    log("train rows %s   validation rows %s   features %d"
        % (f"{int(mtr.sum()):,}", f"{int(mva.sum()):,}", Xall.shape[1]))
    log("")

    probas = fit_grid(Xtr, ytr, Xall, SEED)
    rows = score_grid(probas, ds, nov)

    log("=" * 96)
    log("ALL %d CONFIGURATIONS  (sorted by validation net)" % len(rows))
    log("=" * 96)
    log(HDR)
    for r in sorted(rows, key=lambda z: -z["valid_net"]):
        log(fmt(r))
    log("")

    best = max(rows, key=lambda z: z["valid_net"])
    drift = float(ds.y_up[mva].mean())

    # ---- rotation null: what does searching 54 cells buy by itself? ----
    log("=" * 96)
    log("ROTATION NULL  (%d refits of the full grid on rotated labels)"
        % N_NULL)
    log("=" * 96)
    log("Training labels are circularly shifted, which destroys any link to")
    log("the features but keeps their autocorrelation and drift intact.")
    log("")
    rng = np.random.default_rng(SEED)
    n_tr = int(mtr.sum())
    null_best = []
    for i in range(N_NULL):
        shift = int(rng.integers(n_tr // 10, n_tr - n_tr // 10))
        y_rot = np.roll(ytr, shift)
        pr = fit_grid(Xtr, y_rot, Xall, SEED + 1 + i)
        nr = score_grid(pr, ds, nov)
        b = max(nr, key=lambda z: z["valid_net"])
        null_best.append(b["valid_net"])
        log("  rotation %d (shift %6d)   best-of-grid validation net %9.1f"
            "   [%s / %s]" % (i + 1, shift, b["valid_net"], b["model"],
                              b["rule"]))
    null_best = np.array(null_best)
    log("")
    log("  null best-of-grid:  mean %.1f   sd %.1f   max %.1f"
        % (null_best.mean(), null_best.std(ddof=1), null_best.max()))
    log("  real best-of-grid:  %.1f" % best["valid_net"])
    n_ge = int((null_best >= best["valid_net"]).sum())
    p_emp = (n_ge + 1) / (len(null_best) + 1)
    log("  rotations matching or beating the real result: %d of %d"
        "   (empirical p <= %.3f)" % (n_ge, len(null_best), p_emp))
    log("")

    log("=" * 96)
    log("VERDICT")
    log("=" * 96)
    log("  best configuration      %s / %s" % (best["model"], best["rule"]))
    log("  validation gross        %+.1f" % best["valid_gross"])
    log("  validation cost         %+.1f" % -best["valid_cost"])
    log("  validation net          %+.1f" % best["valid_net"])
    log("  validation accuracy     %.4f   (drift base rate %.4f)"
        % (best["valid_acc"], drift))
    log("  validation t(ind)       %+.2f" % best["valid_t"])
    log("  mean position           %+.3f   (+1 would be always_long)"
        % best["mean_pos"])
    log("  baseline to beat        always_long, validation net -0.3")
    log("  null best-of-grid mean  %+.1f" % null_best.mean())
    log("")
    beats_baseline = best["valid_net"] > 0.0
    beats_null = p_emp <= 0.125 and best["valid_net"] > null_best.max()
    if beats_baseline and beats_null:
        log("  -> survives both comparisons. Carry forward to walk-forward.")
    else:
        log("  -> DOES NOT clear the bar. %s"
            % ("Best result is inside the range selection alone produces."
               if not beats_null else "Best result is not profitable."))
    log("")

    with open(os.path.join(out_dir, "models.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "timeframe": TIMEFRAME,
                   "horizon": HORIZON, "generated": stamp,
                   "n_configurations": len(rows), "results": rows,
                   "best": best, "drift": drift,
                   "null_best_of_grid": null_best.tolist(),
                   "empirical_p": p_emp}, fh, indent=2, default=float)
    log("elapsed %.1fs   written: %s" % (time.time() - t_start, out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
