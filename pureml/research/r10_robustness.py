# Author: Scott (ScottX Research)
"""R10 — cost sensitivity, calibration, and performance by year/session/regime.

The brief requires a model to be judged on far more than accuracy. This
supplies the rest: calibration, cost sensitivity, and a breakdown by year, by
trading session and by volatility regime.

It runs on the WALK-FORWARD out-of-sample series from R06, not on an
in-sample fit, so every number here is a genuine out-of-sample number. The
model is `logit_l2_C0.1`, H1 k=8, overlapping book, refit on an expanding
window — fixed in R06 before any of these breakdowns were computed.

The single most important question this answers: **does the loss come from
costs, or from the signal?** If performance at zero cost is still negative,
no amount of execution improvement, broker shopping or spread negotiation can
rescue it.

Train + validation only. The test split is not read.

Run:  python -m pureml.research.r10_robustness
"""
from __future__ import annotations

import json
import os
import warnings
from datetime import datetime, timezone

import numpy as np

from ..config import ARTIFACT_DIR, SPLIT_TEST, SYMBOL
from ..data.dataset import build_dataset, nonoverlap_mask
from ..models.fit import Preprocessor, build_model, positions_from_proba
from .evaluate import evaluate_positions

TIMEFRAME, HORIZON = "H1", 8
MODEL = ("logit_l2_C0.1", {"kind": "logit", "penalty": "l2", "C": 0.1})
SEED = 20260828
MIN_TRAIN, STEP = 12_000, 1_500
COST_MULTIPLIERS = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def log(s):
    print(s, flush=True)


def main():
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r10_robustness_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R10 — ROBUSTNESS, COSTS, CALIBRATION, REGIMES  (%s %s, k=%d)"
        % (SYMBOL, TIMEFRAME, HORIZON))
    log("All numbers are walk-forward out-of-sample. Test split not read.")
    log("")

    ds = build_dataset(TIMEFRAME, HORIZON)
    nov = nonoverlap_mask(ds)
    avail = np.flatnonzero(ds.split != SPLIT_TEST)
    n = len(avail)
    X, y = ds.X, ds.y_up
    name, spec = MODEL

    pos = np.zeros(len(ds))
    proba = np.full(len(ds), np.nan)
    oos = np.zeros(len(ds), dtype=bool)
    for s in range(MIN_TRAIN, n - STEP + 1, STEP):
        tr = avail[:max(0, s - HORIZON)]
        fold = avail[s:s + STEP]
        warm = avail[max(0, s - HORIZON):s + STEP]
        pre = Preprocessor.fit(X[tr])
        clf = build_model(spec, SEED)
        clf.fit(pre.transform(X[tr]), y[tr])
        pr = clf.predict_proba(pre.transform(X[warm]))[:, 1]
        pos[fold] = positions_from_proba(pr, deadband=0.0,
                                         hold=HORIZON)[-len(fold):]
        proba[fold] = pr[-len(fold):]
        oos[fold] = True

    al = np.where(oos, 1.0, 0.0)
    log("out-of-sample bars: %s" % f"{int(oos.sum()):,}")
    log("")

    # ---------- 1. cost sensitivity ----------
    log("=" * 96)
    log("COST SENSITIVITY")
    log("=" * 96)
    log("  %-14s %12s %12s %12s" % ("cost x", "model net", "always_long",
                                    "model gross"))
    cs = {}
    for cm in COST_MULTIPLIERS:
        r = evaluate_positions(pos, ds, oos, nov, cost_multiplier=cm)
        ra = evaluate_positions(al, ds, oos, nov, cost_multiplier=cm)
        cs[cm] = {"model_net": r["total_net"], "long_net": ra["total_net"],
                  "gross": r["gross_total"]}
        log("  %-14s %12.1f %12.1f %12.1f"
            % ("%.1fx spread" % cm, r["total_net"], ra["total_net"],
               r["gross_total"]))
    log("")
    z = cs[0.0]["model_net"]
    if z <= 0:
        log("  **At ZERO cost the model still loses %.1f.** The loss is not a"
            % -z)
        log("  cost problem. No spread improvement, execution upgrade or")
        log("  broker change can rescue a negative gross signal.")
    else:
        be = None
        for cm in COST_MULTIPLIERS:
            if cs[cm]["model_net"] <= 0:
                be = cm
                break
        log("  Gross is positive (%.1f). It turns negative at roughly %s the"
            % (z, "%.1fx" % be if be else ">3x"))
        log("  modelled spread — which is the margin available for slippage.")
    log("")

    # ---------- 2. calibration ----------
    log("=" * 96)
    log("CALIBRATION  (does P(up) mean anything?)")
    log("=" * 96)
    mi = oos & nov
    p, yv = proba[mi], ds.y_up[mi]
    ok = np.isfinite(p)
    p, yv = p[ok], yv[ok]
    edges = np.quantile(p, np.linspace(0, 1, 11))
    edges[0], edges[-1] = -np.inf, np.inf
    b = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, 9)
    log("  %-6s %10s %12s %12s %9s" % ("decile", "n", "mean P(up)",
                                       "actual P(up)", "error"))
    calib = []
    for k in range(10):
        m = b == k
        if m.sum() < 5:
            continue
        pm, am = float(p[m].mean()), float(yv[m].mean())
        calib.append({"decile": k + 1, "n": int(m.sum()), "pred": pm,
                      "actual": am})
        log("  %-6d %10d %12.4f %12.4f %+9.4f"
            % (k + 1, int(m.sum()), pm, am, am - pm))
    if calib:
        rho = np.corrcoef([c["pred"] for c in calib],
                          [c["actual"] for c in calib])[0, 1]
        lo, hi = calib[0], calib[-1]
        log("")
        log("  correlation between predicted and actual across deciles: %+.3f"
            % rho)
        log("  bottom decile actual %.4f  vs  top decile actual %.4f  "
            "(spread %+.4f)" % (lo["actual"], hi["actual"],
                                hi["actual"] - lo["actual"]))
        log("  A calibrated, informative model needs a strongly positive")
        log("  correlation AND a wide top-minus-bottom spread. Both are")
        log("  required: monotone-but-flat is useless for sizing.")
    log("")

    # ---------- 3. by year ----------
    dt = ds.time / 1000.0
    yrs = np.array([datetime.fromtimestamp(t, tz=timezone.utc).year
                    for t in dt])
    log("=" * 96)
    log("BY YEAR")
    log("=" * 96)
    log("  %-6s %9s %12s %12s %10s" % ("year", "bars", "model net",
                                       "always_long", "model acc"))
    by_year = {}
    for yr in sorted(set(yrs[oos])):
        m = oos & (yrs == yr)
        if m.sum() < 100:
            continue
        r = evaluate_positions(pos, ds, m, nov)
        ra = evaluate_positions(al, ds, m, nov)
        by_year[int(yr)] = {"net": r["total_net"], "long": ra["total_net"],
                            "acc": r["accuracy"], "n": int(m.sum())}
        log("  %-6d %9s %12.1f %12.1f %10.4f"
            % (yr, f"{int(m.sum()):,}", r["total_net"], ra["total_net"],
               r["accuracy"]))
    log("")

    # ---------- 4. by session ----------
    hours = np.array([datetime.fromtimestamp(t, tz=timezone.utc).hour
                      for t in dt])
    sessions = {"Asian (00-07 UTC)": (hours >= 0) & (hours < 8),
                "London (08-12 UTC)": (hours >= 8) & (hours < 13),
                "NY overlap (13-16)": (hours >= 13) & (hours < 17),
                "Late US (17-23)": (hours >= 17)}
    log("=" * 96)
    log("BY SESSION")
    log("=" * 96)
    log("  %-20s %9s %12s %12s %10s" % ("session", "bars", "model net",
                                        "always_long", "model acc"))
    by_sess = {}
    for sname, sm in sessions.items():
        m = oos & sm
        if m.sum() < 100:
            continue
        r = evaluate_positions(pos, ds, m, nov)
        ra = evaluate_positions(al, ds, m, nov)
        by_sess[sname] = {"net": r["total_net"], "long": ra["total_net"],
                          "acc": r["accuracy"], "n": int(m.sum())}
        log("  %-20s %9s %12.1f %12.1f %10.4f"
            % (sname, f"{int(m.sum()):,}", r["total_net"], ra["total_net"],
               r["accuracy"]))
    log("")

    # ---------- 5. by volatility regime ----------
    j = ds.names.index("vol_24")
    v = ds.X[:, j]
    q = np.quantile(v[oos & np.isfinite(v)], [1 / 3, 2 / 3])
    regimes = {"low vol": np.isfinite(v) & (v <= q[0]),
               "mid vol": np.isfinite(v) & (v > q[0]) & (v <= q[1]),
               "high vol": np.isfinite(v) & (v > q[1])}
    log("=" * 96)
    log("BY VOLATILITY REGIME  (terciles of 24-bar realised vol)")
    log("=" * 96)
    log("  %-12s %9s %12s %12s %10s" % ("regime", "bars", "model net",
                                        "always_long", "model acc"))
    by_reg = {}
    for rname, rm in regimes.items():
        m = oos & rm
        if m.sum() < 100:
            continue
        r = evaluate_positions(pos, ds, m, nov)
        ra = evaluate_positions(al, ds, m, nov)
        by_reg[rname] = {"net": r["total_net"], "long": ra["total_net"],
                         "acc": r["accuracy"], "n": int(m.sum())}
        log("  %-12s %9s %12.1f %12.1f %10.4f"
            % (rname, f"{int(m.sum()):,}", r["total_net"], ra["total_net"],
               r["accuracy"]))
    log("")

    log("=" * 96)
    log("STABILITY VERDICT")
    log("=" * 96)
    pos_y = sum(1 for a in by_year.values() if a["net"] > 0)
    pos_s = sum(1 for a in by_sess.values() if a["net"] > 0)
    pos_r = sum(1 for a in by_reg.values() if a["net"] > 0)
    log("  profitable years    %d of %d" % (pos_y, len(by_year)))
    log("  profitable sessions %d of %d" % (pos_s, len(by_sess)))
    log("  profitable regimes  %d of %d" % (pos_r, len(by_reg)))
    log("  net at zero cost    %+.1f" % cs[0.0]["model_net"])
    log("")

    with open(os.path.join(out_dir, "robustness.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "timeframe": TIMEFRAME,
                   "horizon": HORIZON, "generated": stamp, "model": name,
                   "oos_bars": int(oos.sum()),
                   "cost_sensitivity": {str(k): v for k, v in cs.items()},
                   "calibration": calib, "by_year": by_year,
                   "by_session": by_sess, "by_regime": by_reg},
                  fh, indent=2, default=float)
    log("written: %s" % out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
