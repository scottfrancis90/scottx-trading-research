# Author: Scott (ScottX Research)
"""R03 — build the modelling dataset and prove it is leakage-safe.

Builds H1 / 8-hour-horizon data as decided in R02, then runs the integrity
checks that must pass before any model is allowed to see it:

  1. mechanical lookahead test — features recomputed with future bars
     appended must be bit-identical
  2. no label crosses a split boundary (purging)
  3. splits are chronologically ordered and disjoint
  4. target sanity — drift base rate matches R02
  5. feature health — coverage, degenerate columns, extreme collinearity

Nothing is fitted. No model is trained.

Run:  python -m pureml.research.r03_dataset
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import numpy as np

from ..config import (ARTIFACT_DIR, SPLIT_TEST, SPLIT_TRAIN, SPLIT_VALID,
                      SYMBOL)
from ..data.dataset import (build_dataset, nonoverlap_mask,
                            verify_no_lookahead)

TIMEFRAME, HORIZON = "H1", 8


def log(s):
    print(s, flush=True)


def main():
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r03_dataset_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R03 — DATASET CONSTRUCTION  (%s %s, horizon %d bars)"
        % (SYMBOL, TIMEFRAME, HORIZON))
    log("")

    log("CHECK 1 — mechanical lookahead test")
    ok, msg = verify_no_lookahead(TIMEFRAME, HORIZON)
    log("  %s  %s" % ("PASS" if ok else "FAIL", msg))
    if not ok:
        log("")
        log("ABORT — a feature depends on future bars. Nothing may be")
        log("trained on this dataset until that is fixed.")
        return 1
    log("")

    ds = build_dataset(TIMEFRAME, HORIZON)
    log("rows: %s   features: %d" % (f"{len(ds):,}", ds.X.shape[1]))
    t0 = datetime.fromtimestamp(ds.time[0] / 1000, tz=timezone.utc)
    t1 = datetime.fromtimestamp(ds.time[-1] / 1000, tz=timezone.utc)
    log("span: %s -> %s" % (t0.date(), t1.date()))
    log("")

    log("SPLITS")
    log("  %-11s %9s %9s   %-12s %-12s" % ("split", "rows", "indep.",
                                           "from", "to"))
    counts = {}
    for s in (SPLIT_TRAIN, SPLIT_VALID, SPLIT_TEST):
        m = ds.mask(s)
        ni = int(nonoverlap_mask(ds, s).sum())
        counts[s] = {"rows": int(m.sum()), "independent": ni}
        if m.sum():
            a = datetime.fromtimestamp(ds.time[m][0] / 1000, tz=timezone.utc)
            b = datetime.fromtimestamp(ds.time[m][-1] / 1000, tz=timezone.utc)
            log("  %-11s %9s %9s   %-12s %-12s"
                % (s, f"{int(m.sum()):,}", f"{ni:,}", a.date(), b.date()))
    log("")

    log("CHECK 2 — no label crosses a split boundary")
    viol = 0
    for s_a, s_b in ((SPLIT_TRAIN, SPLIT_VALID), (SPLIT_VALID, SPLIT_TEST)):
        end = ds.time[ds.mask(s_a)].max() if ds.mask(s_a).any() else None
        start = ds.time[ds.mask(s_b)].min() if ds.mask(s_b).any() else None
        if end is not None and start is not None:
            gap_h = (start - end) / 3_600_000.0
            log("  %s -> %s   gap %.1f hours (horizon is %d)"
                % (s_a, s_b, gap_h, HORIZON))
            if gap_h < HORIZON:
                viol += 1
    log("  %s" % ("PASS — purging left an adequate gap" if viol == 0
                  else "FAIL — a label can span the boundary"))
    log("")

    log("CHECK 3 — splits are ordered and disjoint")
    order_ok = True
    prev_max = -1
    for s in (SPLIT_TRAIN, SPLIT_VALID, SPLIT_TEST):
        m = ds.mask(s)
        if not m.any():
            continue
        if ds.time[m].min() <= prev_max:
            order_ok = False
        prev_max = max(prev_max, int(ds.time[m].max()))
    log("  %s" % ("PASS" if order_ok else "FAIL — splits overlap in time"))
    log("")

    log("CHECK 4 — target sanity")
    for s in (SPLIT_TRAIN, SPLIT_VALID, SPLIT_TEST):
        m = ds.mask(s)
        if not m.any():
            continue
        log("  %-11s P(up)=%.4f  mean ret=%+.6f  mean |move|=$%.3f  "
            "median spread=$%.3f"
            % (s, ds.y_up[m].mean(), ds.y_ret[m].mean(),
               np.nanmean(ds.fwd_move[m]), float(np.median(ds.spread[m]))))
    log("  (train P(up) should match R02's H1 k=8 drift of 0.5142)")
    log("")

    log("CHECK 5 — feature health (train only)")
    tr = ds.mask(SPLIT_TRAIN)
    Xtr = ds.X[tr]
    cov = 1.0 - np.isnan(Xtr).mean(axis=0)
    sd = np.nanstd(Xtr, axis=0)
    bad_cov = [ds.names[i] for i in range(len(ds.names)) if cov[i] < 0.95]
    degen = [ds.names[i] for i in range(len(ds.names))
             if not np.isfinite(sd[i]) or sd[i] < 1e-12]
    log("  coverage < 95%%: %s" % (", ".join(bad_cov) if bad_cov else "none"))
    log("  degenerate (zero variance): %s" % (", ".join(degen) if degen
                                              else "none"))

    Z = np.where(np.isnan(Xtr), np.nanmean(Xtr, axis=0), Xtr)
    Z = (Z - Z.mean(0)) / np.where(Z.std(0) > 0, Z.std(0), 1.0)
    C = np.corrcoef(Z, rowvar=False)
    pairs = []
    for i in range(len(ds.names)):
        for j in range(i + 1, len(ds.names)):
            if abs(C[i, j]) > 0.98:
                pairs.append((ds.names[i], ds.names[j], float(C[i, j])))
    log("  |corr| > 0.98 pairs: %s"
        % ("; ".join("%s~%s %.3f" % p for p in pairs[:6]) if pairs
           else "none"))
    log("")

    np.savez_compressed(
        os.path.join(out_dir, "dataset.npz"),
        time=ds.time, X=ds.X, y_ret=ds.y_ret, y_up=ds.y_up,
        fwd_move=ds.fwd_move, spread=ds.spread, close=ds.close,
        split=ds.split.astype("U12"), names=np.array(ds.names))
    with open(os.path.join(out_dir, "summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "timeframe": TIMEFRAME,
                   "horizon": HORIZON, "generated": stamp,
                   "rows": len(ds), "n_features": ds.X.shape[1],
                   "feature_names": ds.names, "splits": counts,
                   "lookahead_check": msg,
                   "low_coverage": bad_cov, "degenerate": degen,
                   "collinear_pairs": pairs}, fh, indent=2)
    log("written: %s" % out_dir)
    log("")
    log("Dataset is built and integrity-checked. No model has seen it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
