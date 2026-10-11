# Author: Scott (ScottX Research)
"""R06 — walk-forward evaluation.

R05 used one train/validation boundary. A single boundary can be unlucky:
2021-08 to 2023-02 is one particular regime, and a model could fail there and
work elsewhere. Walk-forward removes that objection by refitting repeatedly
and trading only the bars immediately after each refit.

Two things are tested, and they are different questions.

  FIXED       three pre-registered models, refitted each fold, deployed with
              one pre-registered position rule. Tests the MODEL.
  ADAPTIVE    at each fold, all 54 configurations are scored on an inner
              validation window carved from the end of the training data, the
              best is selected, refitted on the full window, and deployed.
              Tests the SELECTION PROCEDURE — i.e. whether the whole research
              pipeline, run honestly, produces something that works.

`always_long` is run through the identical fold machinery as the comparator.

Purging: the last `horizon` rows of every training window are dropped, since
their labels reach into the window being traded. The same applies to the inner
validation boundary.

**The test split is excluded entirely.** Folds run over train + validation
only.

Run:  python -m pureml.research.r06_walkforward
"""
from __future__ import annotations

import json
import os
import time
import warnings
from datetime import datetime, timezone

import numpy as np

from ..config import ARTIFACT_DIR, SPLIT_TEST, SYMBOL
from ..data.dataset import build_dataset, nonoverlap_mask
from ..models.fit import (MODEL_GRID, POSITION_GRID, Preprocessor,
                          build_model, positions_from_proba)
from .evaluate import evaluate_positions

TIMEFRAME, HORIZON = "H1", 8
SEED = 20260828

MIN_TRAIN = 12_000        # ~1.7 years of H1 bars before the first fold
STEP = 1_500              # bars traded per fold (~2 months)
INNER_VALID = 3_000       # inner validation window for ADAPTIVE selection

#: Pre-registered fixed models — one per family, chosen for representativeness
#: before any fold was run, NOT because they scored well in R05.
FIXED = ["logit_l2_C0.1", "logit_l1_C0.01", "hgb_d2_lr0.03"]
FIXED_RULE = "d0.00_hold"

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

SPEC = dict(MODEL_GRID)
RULE = dict(POSITION_GRID)


def log(s):
    print(s, flush=True)


def _fit_predict(name, tr_rows, pred_rows, X, y, seed):
    pre = Preprocessor.fit(X[tr_rows])
    clf = build_model(SPEC[name], seed)
    clf.fit(pre.transform(X[tr_rows]), y[tr_rows])
    return clf.predict_proba(pre.transform(X[pred_rows]))[:, 1]


def main():
    t0 = time.time()
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r06_walkforward_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R06 — WALK-FORWARD  (%s %s, horizon %d)" % (SYMBOL, TIMEFRAME,
                                                     HORIZON))
    log("Folds cover train + validation. The test split is excluded.")
    log("")

    ds = build_dataset(TIMEFRAME, HORIZON)
    nov = nonoverlap_mask(ds)
    avail = np.flatnonzero(ds.split != SPLIT_TEST)
    n = len(avail)
    X, y = ds.X, ds.y_up

    starts = list(range(MIN_TRAIN, n - STEP + 1, STEP))
    log("usable rows %s   min train %s   step %s   folds %d"
        % (f"{n:,}", f"{MIN_TRAIN:,}", f"{STEP:,}", len(starts)))
    log("fixed models: %s   rule: %s" % (", ".join(FIXED), FIXED_RULE))
    log("adaptive: best of %d configs chosen on a %s-bar inner window"
        % (len(MODEL_GRID) * len(POSITION_GRID), f"{INNER_VALID:,}"))
    log("")

    series = {k: np.zeros(len(ds)) for k in FIXED + ["adaptive"]}
    oos = np.zeros(len(ds), dtype=bool)
    fold_log = []

    for fi, s in enumerate(starts):
        tr = avail[:max(0, s - HORIZON)]                 # purged
        fold = avail[s:s + STEP]
        warm = avail[max(0, s - HORIZON):s + STEP]       # for the hold book
        oos[fold] = True

        # ---- FIXED ----
        row = {"fold": fi + 1,
               "from": int(ds.time[fold[0]]), "to": int(ds.time[fold[-1]]),
               "n_train": len(tr), "n_oos": len(fold)}
        for name in FIXED:
            pr = _fit_predict(name, tr, warm, X, y, SEED)
            pos = positions_from_proba(pr, **RULE[FIXED_RULE])
            series[name][fold] = pos[-len(fold):]

        # ---- ADAPTIVE: select on an inner window, then refit and deploy ----
        iv_end = len(tr)
        iv_start = max(1, iv_end - INNER_VALID)
        inner_tr = tr[:max(0, iv_start - HORIZON)]
        inner_va = tr[iv_start:iv_end]
        best, best_net = None, -np.inf
        if len(inner_tr) > 500 and len(inner_va) > 200:
            iv_mask = np.zeros(len(ds), dtype=bool)
            iv_mask[inner_va] = True
            iv_warm = tr[max(0, iv_start - HORIZON):iv_end]
            for mname, _ in MODEL_GRID:
                pr = _fit_predict(mname, inner_tr, iv_warm, X, y, SEED)
                for rname, rspec in POSITION_GRID:
                    p = positions_from_proba(pr, **rspec)
                    full = np.zeros(len(ds))
                    full[inner_va] = p[-len(inner_va):]
                    r = evaluate_positions(full, ds, iv_mask, nov)
                    if r and r["total_net"] > best_net:
                        best_net, best = r["total_net"], (mname, rname)
        if best is None:
            best = (FIXED[0], FIXED_RULE)
        pr = _fit_predict(best[0], tr, warm, X, y, SEED)
        series["adaptive"][fold] = positions_from_proba(
            pr, **RULE[best[1]])[-len(fold):]
        row["adaptive_choice"] = "%s / %s" % best
        row["adaptive_inner_net"] = float(best_net) if np.isfinite(best_net) \
            else None
        fold_log.append(row)
        log("  fold %2d  %s -> %s  train %6d  chose %-16s %-12s"
            % (fi + 1,
               datetime.fromtimestamp(row["from"] / 1000,
                                      tz=timezone.utc).date(),
               datetime.fromtimestamp(row["to"] / 1000,
                                      tz=timezone.utc).date(),
               len(tr), best[0], best[1]))

    series["always_long"] = np.where(oos, 1.0, 0.0)
    log("")

    # ---- per-fold P&L for every strategy ----
    log("=" * 100)
    log("PER-FOLD OUT-OF-SAMPLE NET")
    log("=" * 100)
    names = FIXED + ["adaptive", "always_long"]
    log("  %-6s %-12s %10s %10s %10s %10s %10s"
        % ("fold", "to", *[nm[:10] for nm in names]))
    per_fold = {nm: [] for nm in names}
    for fi, s in enumerate(starts):
        fold = avail[s:s + STEP]
        fm = np.zeros(len(ds), dtype=bool)
        fm[fold] = True
        vals = []
        for nm in names:
            r = evaluate_positions(series[nm], ds, fm, nov)
            per_fold[nm].append(r["total_net"])
            vals.append(r["total_net"])
        log("  %-6d %-12s %10.1f %10.1f %10.1f %10.1f %10.1f"
            % (fi + 1, datetime.fromtimestamp(
                int(ds.time[fold[-1]]) / 1000, tz=timezone.utc).date(),
               *vals))
    log("")

    # ---- aggregate ----
    log("=" * 100)
    log("AGGREGATE OVER ALL FOLDS  (%s out-of-sample bars)"
        % f"{int(oos.sum()):,}")
    log("=" * 100)
    log("  %-14s %10s %10s %10s %8s %8s %7s %8s %8s"
        % ("strategy", "gross", "cost", "net", "acc", "t(ind)", "turn",
           "folds+", "maxDD"))
    summary = {}
    for nm in names:
        r = evaluate_positions(series[nm], ds, oos, nov)
        pf = np.array(per_fold[nm])
        wins = int((pf > 0).sum())
        summary[nm] = dict(r, folds_positive=wins, n_folds=len(pf),
                           fold_mean=float(pf.mean()),
                           fold_t=float(pf.mean() / (pf.std(ddof=1) /
                                                     np.sqrt(len(pf))))
                           if pf.std(ddof=1) > 0 else float("nan"))
        log("  %-14s %10.1f %10.1f %10.1f %8.4f %8.2f %7.3f %8s %8.1f"
            % (nm, r["gross_total"], -r["cost_total"], r["total_net"],
               r["accuracy"], r["t_independent"], r["turnover"],
               "%d/%d" % (wins, len(pf)), r["max_drawdown"]))
    log("")
    log("  fold-level t-statistic (mean fold net / its standard error):")
    for nm in names:
        log("    %-14s mean %+9.1f per fold   t = %+.2f"
            % (nm, summary[nm]["fold_mean"], summary[nm]["fold_t"]))
    log("")

    log("=" * 100)
    log("VERDICT")
    log("=" * 100)
    al = summary["always_long"]
    winners = [nm for nm in names[:-1]
               if summary[nm]["total_net"] > max(0.0, al["total_net"])]
    log("  always_long over the same bars: net %+.1f" % al["total_net"])
    if winners:
        for nm in winners:
            log("  %s beats it: net %+.1f (t=%+.2f over folds)"
                % (nm, summary[nm]["total_net"], summary[nm]["fold_t"]))
        log("  -> carry forward; test split still sealed.")
    else:
        log("  No model beats always_long or zero out of sample.")
        log("  -> walk-forward confirms R05. The test split stays sealed.")
    log("")

    with open(os.path.join(out_dir, "walkforward.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "timeframe": TIMEFRAME,
                   "horizon": HORIZON, "generated": stamp,
                   "min_train": MIN_TRAIN, "step": STEP,
                   "inner_valid": INNER_VALID, "fixed": FIXED,
                   "fixed_rule": FIXED_RULE, "folds": fold_log,
                   "per_fold_net": {k: [float(x) for x in v]
                                    for k, v in per_fold.items()},
                   "summary": summary}, fh, indent=2, default=float)
    log("elapsed %.1fs   written: %s" % (time.time() - t0, out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
