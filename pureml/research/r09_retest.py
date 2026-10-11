# Author: Scott (ScottX Research)
"""R09 — re-test the three cells that survived the R08 sweep.

R08 found 3 of 32 cells with positive validation net:

    H4  k=1   hgb_d2_lr0.03   +284.8
    H4  k=8   hgb_d2_lr0.03    +97.1
    M30 k=16  logit_l2_C0.1    +55.3

R08's own pre-registered rule was that no cell graduates on the strength of
the sweep — a survivor must pass the two tests that killed H1/k=8:

  1. ROTATION NULL. Refit the same model on circularly rotated training
     labels many times. If rotated labels routinely produce a comparable
     validation result, the cell is selection noise.
  2. WALK-FORWARD. Refit on an expanding window and trade only the bars
     immediately after each refit. A real effect survives repeated refitting;
     a lucky split does not.

Nothing is tuned here. The model, the position rule and the cell definition
are all inherited from R08 exactly as they were.

Train -> validation only. The test split is not read.

Run:  python -m pureml.research.r09_retest
"""
from __future__ import annotations

import json
import os
import time
import warnings
from datetime import datetime, timezone

import numpy as np

from ..config import (ARTIFACT_DIR, DATA_START, SPLIT_TEST, SPLIT_TRAIN,
                      SPLIT_VALID, SYMBOL)
from ..data.dataset import build_dataset, nonoverlap_mask
from ..data.loader import aggregate, load_raw
from ..models.fit import Preprocessor, build_model, positions_from_proba
from .evaluate import evaluate_positions

#: (timeframe, horizon, model name, model spec) — copied from R08 unchanged.
CELLS = [
    ("H4", 1, "hgb_d2_lr0.03", {"kind": "hgb", "max_depth": 2, "lr": 0.03}),
    ("H4", 8, "hgb_d2_lr0.03", {"kind": "hgb", "max_depth": 2, "lr": 0.03}),
    ("M30", 16, "logit_l2_C0.1", {"kind": "logit", "penalty": "l2",
                                  "C": 0.1}),
]
SEED = 20260828
N_ROTATIONS = 12
N_FOLDS = 12

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def log(s):
    print(s, flush=True)


def _positions(spec, tr_rows, pred_rows, X, y, k, seed):
    pre = Preprocessor.fit(X[tr_rows])
    clf = build_model(spec, seed)
    clf.fit(pre.transform(X[tr_rows]), y[tr_rows])
    pr = clf.predict_proba(pre.transform(X[pred_rows]))[:, 1]
    return positions_from_proba(pr, deadband=0.0, hold=k)


def main():
    t0 = time.time()
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r09_retest_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R09 — RE-TEST OF R08 SURVIVORS  (%s)" % SYMBOL)
    log("Rotation null + walk-forward. Nothing is tuned. Test not read.")
    log("")

    base = load_raw("M1").slice_from(DATA_START)
    agg = {}
    out = []

    for tf, k, mname, spec in CELLS:
        if tf not in agg:
            agg[tf] = base if tf == "M1" else aggregate(base, tf)
        ds = build_dataset(tf, k, bars=agg[tf])
        nov = nonoverlap_mask(ds)
        mtr, mva = ds.mask(SPLIT_TRAIN), ds.mask(SPLIT_VALID)
        rows_tr = np.flatnonzero(mtr)
        X, y = ds.X, ds.y_up

        log("=" * 100)
        log("CELL  %s  k=%d  %s      train %s   validation %s"
            % (tf, k, mname, f"{int(mtr.sum()):,}", f"{int(mva.sum()):,}"))
        log("=" * 100)

        # ---- headline (reproduce R08) ----
        allrows = np.arange(len(ds))
        pos = _positions(spec, rows_tr, allrows, X, y, k, SEED)
        real = evaluate_positions(pos, ds, mva, nov)
        log("  R08 headline reproduced: validation net %+.1f  gross %+.1f  "
            "acc %.4f  t(ind) %+.2f"
            % (real["total_net"], real["gross_total"], real["accuracy"],
               real["t_independent"]))
        log("")

        # ---- 1. rotation null ----
        log("  ROTATION NULL (%d refits on circularly rotated labels)"
            % N_ROTATIONS)
        rng = np.random.default_rng(SEED + k)
        n_tr = len(rows_tr)
        nulls = []
        for i in range(N_ROTATIONS):
            sh = int(rng.integers(n_tr // 10, n_tr - n_tr // 10))
            y_rot = y.copy()
            y_rot[rows_tr] = np.roll(y[rows_tr], sh)
            p = _positions(spec, rows_tr, allrows, X, y_rot, k, SEED + 1 + i)
            nulls.append(evaluate_positions(p, ds, mva, nov)["total_net"])
        nulls = np.array(nulls)
        n_ge = int((nulls >= real["total_net"]).sum())
        p_emp = (n_ge + 1) / (len(nulls) + 1)
        log("    null net: mean %+.1f   sd %.1f   min %+.1f   max %+.1f"
            % (nulls.mean(), nulls.std(ddof=1), nulls.min(), nulls.max()))
        log("    real net: %+.1f" % real["total_net"])
        log("    rotations matching or beating it: %d of %d   "
            "(empirical p <= %.3f)" % (n_ge, len(nulls), p_emp))
        log("")

        # ---- 2. walk-forward ----
        avail = np.flatnonzero(ds.split != SPLIT_TEST)
        n = len(avail)
        min_train = int(0.35 * n)
        step = max(1, (n - min_train) // N_FOLDS)
        starts = list(range(min_train, n - step + 1, step))
        wf = np.zeros(len(ds))
        oos = np.zeros(len(ds), dtype=bool)
        per_fold = []
        for s in starts:
            tr = avail[:max(0, s - k)]
            fold = avail[s:s + step]
            warm = avail[max(0, s - k):s + step]
            if len(tr) < 500:
                continue
            p = _positions(spec, tr, warm, X, y, k, SEED)
            wf[fold] = p[-len(fold):]
            oos[fold] = True
            fm = np.zeros(len(ds), dtype=bool)
            fm[fold] = True
            per_fold.append(evaluate_positions(wf, ds, fm, nov)["total_net"])
        per_fold = np.array(per_fold)
        rwf = evaluate_positions(wf, ds, oos, nov)
        ral = evaluate_positions(np.where(oos, 1.0, 0.0), ds, oos, nov)
        fold_t = (float(per_fold.mean() / (per_fold.std(ddof=1) /
                                           np.sqrt(len(per_fold))))
                  if len(per_fold) > 2 and per_fold.std(ddof=1) > 0
                  else float("nan"))
        log("  WALK-FORWARD (%d folds, %s out-of-sample bars, min train %s)"
            % (len(per_fold), f"{int(oos.sum()):,}", f"{min_train:,}"))
        log("    model        net %+9.1f   gross %+9.1f   acc %.4f   "
            "folds+ %d/%d   fold t %+.2f"
            % (rwf["total_net"], rwf["gross_total"], rwf["accuracy"],
               int((per_fold > 0).sum()), len(per_fold), fold_t))
        log("    always_long  net %+9.1f   over the identical bars"
            % ral["total_net"])
        log("")

        survives = (p_emp <= 0.1 and real["total_net"] > nulls.max()
                    and rwf["total_net"] > max(0.0, ral["total_net"]))
        log("  VERDICT: %s" % ("SURVIVES both tests" if survives
                               else "FAILS"))
        if not survives:
            reasons = []
            if p_emp > 0.1 or real["total_net"] <= nulls.max():
                reasons.append("rotated labels reproduce it")
            if rwf["total_net"] <= 0:
                reasons.append("loses money under walk-forward")
            elif rwf["total_net"] <= ral["total_net"]:
                reasons.append("walk-forward does not beat always_long")
            log("           %s" % "; ".join(reasons))
        log("")

        out.append({"timeframe": tf, "horizon": k, "model": mname,
                    "valid_net": real["total_net"],
                    "valid_gross": real["gross_total"],
                    "valid_t": real["t_independent"],
                    "null_mean": float(nulls.mean()),
                    "null_max": float(nulls.max()),
                    "null_sd": float(nulls.std(ddof=1)),
                    "empirical_p": p_emp,
                    "wf_net": rwf["total_net"], "wf_gross": rwf["gross_total"],
                    "wf_acc": rwf["accuracy"],
                    "wf_folds_positive": int((per_fold > 0).sum()),
                    "wf_n_folds": len(per_fold), "wf_fold_t": fold_t,
                    "wf_always_long": ral["total_net"],
                    "survives": bool(survives)})

    log("=" * 100)
    log("SUMMARY")
    log("=" * 100)
    surv = [r for r in out if r["survives"]]
    for r in out:
        log("  %-4s k=%-3d %-15s  valid %+8.1f | null max %+8.1f | "
            "walk-fwd %+8.1f | %s"
            % (r["timeframe"], r["horizon"], r["model"], r["valid_net"],
               r["null_max"], r["wf_net"],
               "SURVIVES" if r["survives"] else "fails"))
    log("")
    if surv:
        log("  %d cell(s) survive. These are the only candidates for the"
            % len(surv))
        log("  final test-set evaluation.")
    else:
        log("  NO CELL SURVIVES. Every apparent winner in the R08 sweep is")
        log("  explained by selection across 32 cells. The test split stays")
        log("  sealed — there is nothing that has earned an evaluation on it.")
    log("")

    with open(os.path.join(out_dir, "retest.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "generated": stamp,
                   "n_rotations": N_ROTATIONS, "cells": out},
                  fh, indent=2, default=float)
    log("elapsed %.1fs   written: %s" % (time.time() - t0, out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
