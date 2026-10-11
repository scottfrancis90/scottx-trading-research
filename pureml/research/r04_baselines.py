# Author: Scott (ScottX Research)
"""R04 — baselines. Establish what must be beaten before any model is fitted.

If ML cannot beat these out of sample, that is the finding and it will be
reported as such.

Baselines
---------
always_long     permanently +1. Captures pure drift; the single most
                important comparator, because gold rose 40% in training.
always_short    permanently -1. Reported so the drift asymmetry is visible.
momentum_k      sign of the trailing k-bar return — naive continuation.
reversion_k     the negation — naive mean reversion.
coin_flip       deterministic pseudo-random signs, seeded. The null.
vol_filtered    always_long, but flat when short-term vol is in the top
                quintile of its own trailing distribution. Tests whether a
                trivially simple risk filter helps.

Train and validation only. The test split is not read.

Run:  python -m pureml.research.r04_baselines
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import numpy as np

from ..config import ARTIFACT_DIR, SPLIT_TRAIN, SPLIT_VALID, SYMBOL
from ..data.dataset import build_dataset, nonoverlap_mask
from .evaluate import HEADER, evaluate_positions, format_row

TIMEFRAME, HORIZON = "H1", 8
SEED = 20260828


def log(s):
    print(s, flush=True)


def build_baselines(ds):
    n = len(ds)
    names = ds.names
    col = {nm: ds.X[:, i] for i, nm in enumerate(names)}
    out = {}

    out["always_long"] = np.ones(n)
    out["always_short"] = -np.ones(n)

    rng = np.random.default_rng(SEED)
    out["coin_flip"] = rng.choice([-1.0, 1.0], size=n)

    for k in (1, 8, 24):
        s = np.sign(col["ret_%d" % k]) if ("ret_%d" % k) in col else None
        if s is not None:
            out["momentum_%d" % k] = np.where(np.isnan(s), 0.0, s)
            out["reversion_%d" % k] = -out["momentum_%d" % k]

    # always long, flat when recent vol is extreme relative to its own past
    v = col["vol_24"]
    thr = np.full(n, np.nan)
    w = 500
    for i in range(w, n):
        thr[i] = np.nanquantile(v[i - w:i], 0.80)
    q = np.where(np.isnan(thr) | np.isnan(v), 1.0,
                 np.where(v > thr, 0.0, 1.0))
    out["long_vol_filtered"] = q
    return out


def main():
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r04_baselines_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R04 — BASELINES  (%s %s, horizon %d)" % (SYMBOL, TIMEFRAME, HORIZON))
    log("Train and validation only. Test is not read.")
    log("")

    ds = build_dataset(TIMEFRAME, HORIZON)
    base = build_baselines(ds)
    nov = nonoverlap_mask(ds)

    results = {}
    for split in (SPLIT_TRAIN, SPLIT_VALID):
        m = ds.mask(split)
        req = 0.5 + float(np.median(ds.spread[m])) / (
            2.0 * float(np.nanmean(ds.fwd_move[m])))
        bh = float(ds.close[m][-1] - ds.close[m][0])
        log("=" * 112)
        log("%s   rows=%s   independent=%s   required acc=%.4f   drift=%.4f"
            "   buy&hold=$%+.1f/oz"
            % (split.upper(), f"{int(m.sum()):,}",
               f"{int((nonoverlap_mask(ds, split)).sum()):,}",
               req, float(ds.y_up[m].mean()), bh))
        log("=" * 112)
        log(HEADER)
        results[split] = {"required_accuracy": req}
        for name, pos in base.items():
            r = evaluate_positions(pos, ds, m, nov)
            results[split][name] = r
            log(format_row(name, r))
        log("")

    log("=" * 112)
    log("READING THIS TABLE")
    log("=" * 112)
    log("  acc    directional accuracy of the signal vs the 8-bar target")
    log("  drift  base rate of positive forward returns — what 'acc' must")
    log("         beat, NOT 0.5")
    log("  $/bar  net profit per bar after turnover costs")
    log("  t(ind) t-statistic on NON-OVERLAPPING bars only")
    log("  turn   mean |position change| per bar — the cost driver")
    log("")
    v = results[SPLIT_VALID]
    log("THE BAR FOR ANY MODEL (validation):")
    log("  beat always_long   net $%+.1f   t=%+.2f"
        % (v["always_long"]["total_net"],
           v["always_long"]["t_independent"]))
    log("  with accuracy above %.4f (the drift base rate)"
        % v["always_long"]["drift_base_rate"])
    log("")

    with open(os.path.join(out_dir, "baselines.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "timeframe": TIMEFRAME,
                   "horizon": HORIZON, "generated": stamp,
                   "results": results}, fh, indent=2, default=float)
    log("written: %s" % out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
