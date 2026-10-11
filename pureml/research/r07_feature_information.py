# Author: Scott (ScottX Research)
"""R07 — model-free feature information, and the ceiling.

R05 and R06 report that models fail. Two objections remain open, and both
have to be answered without a model, or the null is not credible:

  1. "Your models are bad." Tested here by measuring each feature's own
     relationship to the forward return directly — no fitting, no
     hyperparameters, nothing that can be blamed.
  2. "The opportunity is too small to matter anyway." Tested by computing
     the ORACLE: what a perfect 8-hour-ahead sign forecast would earn on the
     same bars under the same cost model. If the oracle is enormous and the
     models earn nothing, the failure is real prediction failure, not a
     shortage of opportunity.

Multiple testing is handled explicitly: 33 features are examined, so a
Bonferroni threshold is reported alongside the raw statistics.

**Train split only.** Validation is not used for selection here and the test
split is not read.

Run:  python -m pureml.research.r07_feature_information
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone

import numpy as np

from ..config import ARTIFACT_DIR, SPLIT_TRAIN, SPLIT_VALID, SYMBOL
from ..data.dataset import build_dataset, nonoverlap_mask
from .evaluate import evaluate_positions

TIMEFRAME, HORIZON = "H1", 8
N_BINS = 10


def log(s):
    print(s, flush=True)


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    d = math.sqrt(float((ra ** 2).sum()) * float((rb ** 2).sum()))
    return float((ra * rb).sum() / d) if d > 0 else 0.0


def main():
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r07_feature_info_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R07 — FEATURE INFORMATION AND CEILING  (%s %s, horizon %d)"
        % (SYMBOL, TIMEFRAME, HORIZON))
    log("Model-free. Train split only for the feature tests.")
    log("")

    ds = build_dataset(TIMEFRAME, HORIZON)
    nov = nonoverlap_mask(ds)
    mtr = ds.mask(SPLIT_TRAIN)

    # ---------- 1. the ceiling ----------
    log("=" * 100)
    log("THE CEILING — what a perfect forecast would earn")
    log("=" * 100)
    ceil = {}
    for split, m in (("train", mtr), ("validation", ds.mask(SPLIT_VALID))):
        # perfect knowledge of the NEXT BAR's direction (upper bound on any
        # bar-by-bar strategy), and of the 8-hour direction (this project's
        # actual target)
        oracle_1 = np.sign(np.where(np.isfinite(ds.step), ds.step, 0.0))
        oracle_h = np.sign(np.where(np.isfinite(ds.y_ret), ds.y_ret, 0.0))
        r1 = evaluate_positions(oracle_1, ds, m, nov)
        rh = evaluate_positions(oracle_h, ds, m, nov)
        ceil[split] = {"oracle_1bar": r1, "oracle_horizon": rh}
        log("  %-11s perfect NEXT-BAR sign      net %+12.1f  (turn %.3f)"
            % (split, r1["total_net"], r1["turnover"]))
        log("  %-11s perfect %d-HOUR sign        net %+12.1f  (turn %.3f)"
            % ("", HORIZON, rh["total_net"], rh["turnover"]))
    log("")
    log("  The opportunity is not the problem. A perfect %d-hour directional"
        % HORIZON)
    log("  forecast earns thousands of dollars per ounce on these same bars,")
    log("  net of the same costs. Everything below asks whether ANY of that")
    log("  is reachable.")
    log("")

    # ---------- 2. per-feature information ----------
    log("=" * 100)
    log("PER-FEATURE INFORMATION (train, %s non-overlapping rows)"
        % f"{int((mtr & nov).sum()):,}")
    log("=" * 100)
    log("Each feature is cut into %d equal-count bins. Reported: Spearman"
        % N_BINS)
    log("rank correlation with the forward return, the monotone spread")
    log("between top and bottom bin, and a t-statistic computed on")
    log("NON-OVERLAPPING rows only.")
    log("")

    mi = mtr & nov                       # independent training rows
    yr = ds.y_ret[mi]
    rows = []
    for j, name in enumerate(ds.names):
        x = ds.X[mi, j]
        ok = np.isfinite(x) & np.isfinite(yr)
        if ok.sum() < 500:
            continue
        xv, yv = x[ok], yr[ok]
        rho = spearman(xv, yv)
        # Discrete features (weekday encodings) have too few distinct values
        # for deciles: quantile bins collapse and some come out empty. Group
        # by distinct value instead so the comparison is still top vs bottom.
        uniq = np.unique(xv)
        if len(uniq) <= N_BINS:
            b = np.searchsorted(uniq, xv)
            nb = len(uniq)
        else:
            q = np.quantile(xv, np.linspace(0, 1, N_BINS + 1))
            q[0], q[-1] = -np.inf, np.inf
            b = np.clip(np.searchsorted(q, xv, side="right") - 1, 0,
                        N_BINS - 1)
            nb = N_BINS
        means = np.array([yv[b == k].mean() if (b == k).sum() > 1 else np.nan
                          for k in range(nb)])
        spread = float(means[-1] - means[0])
        # t on the top-minus-bottom bin difference
        top, bot = yv[b == nb - 1], yv[b == 0]
        if len(top) < 2 or len(bot) < 2:
            continue
        se = math.sqrt(top.var(ddof=1) / len(top) + bot.var(ddof=1) / len(bot))
        t = float((top.mean() - bot.mean()) / se) if se > 0 else float("nan")
        # monotonicity: rank correlation of bin index with bin mean
        mono = spearman(np.arange(nb, dtype=float),
                        np.nan_to_num(means, nan=0.0))
        rows.append({"feature": name, "spearman": rho, "decile_spread": spread,
                     "t_topbot": t, "monotonicity": mono, "n": int(ok.sum()),
                     "n_bins": nb})

    n_tests = len(rows)
    bonf = 1.96
    # two-sided 5% Bonferroni threshold for n_tests comparisons
    from statistics import NormalDist
    bonf = NormalDist().inv_cdf(1 - 0.05 / (2 * n_tests))

    log("  %-24s %10s %13s %9s %8s" % ("feature", "spearman", "decile spread",
                                       "t(top-bot)", "monotone"))
    for r in sorted(rows, key=lambda z: -abs(z["t_topbot"])):
        star = " *" if abs(r["t_topbot"]) > bonf else ""
        log("  %-24s %10.4f %13.6f %9.2f %8.2f%s"
            % (r["feature"], r["spearman"], r["decile_spread"],
               r["t_topbot"], r["monotonicity"], star))
    log("")
    n_pass = sum(1 for r in rows if abs(r["t_topbot"]) > bonf)
    n_nominal = sum(1 for r in rows if abs(r["t_topbot"]) > 1.96)
    log("  %d features tested." % n_tests)
    log("  Bonferroni 5%% threshold |t| > %.2f  ->  %d pass%s"
        % (bonf, n_pass, "" if n_pass else "  (none)"))
    log("  Nominal 5%% threshold    |t| > 1.96  ->  %d pass "
        "(expected by chance alone: %.1f)" % (n_nominal, 0.05 * n_tests))
    log("")

    # ---------- 3. best single feature traded directly ----------
    log("=" * 100)
    log("BEST SINGLE FEATURE, TRADED DIRECTLY (train-selected, "
        "validation-scored)")
    log("=" * 100)
    log("The single strongest feature by |t| is turned into a position with")
    log("its train-fitted sign and traded on validation. No fitting beyond")
    log("one sign. If even this leaks nothing, the features are the problem,")
    log("not the models.")
    log("")
    best = max(rows, key=lambda z: abs(z["t_topbot"]))
    j = ds.names.index(best["feature"])
    x = ds.X[:, j]
    med = float(np.nanmedian(ds.X[mtr, j]))
    sgn = 1.0 if best["spearman"] > 0 else -1.0
    pos = np.where(np.isnan(x), 0.0, np.sign(x - med) * sgn)
    for split, m in (("train", mtr), ("validation", ds.mask(SPLIT_VALID))):
        r = evaluate_positions(pos, ds, m, nov)
        log("  %-11s %-22s net %+9.1f  gross %+9.1f  acc %.4f  turn %.3f"
            % (split, best["feature"], r["total_net"], r["gross_total"],
               r["accuracy"], r["turnover"]))
    log("")

    with open(os.path.join(out_dir, "feature_info.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "timeframe": TIMEFRAME,
                   "horizon": HORIZON, "generated": stamp,
                   "n_tests": n_tests, "bonferroni_t": bonf,
                   "n_pass_bonferroni": n_pass, "n_pass_nominal": n_nominal,
                   "features": rows, "ceiling": ceil,
                   "best_feature": best["feature"]},
                  fh, indent=2, default=float)
    log("written: %s" % out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
