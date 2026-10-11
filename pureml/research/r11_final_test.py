# Author: Scott (ScottX Research)
"""R11 — THE FINAL TEST EVALUATION. Run exactly once.

The test split (2023-03-01 to 2024-08-23, 8,787 rows) has not been read,
plotted, summarised or trained on at any point in R01-R10. This script is the
first and only time it is used.

PRE-REGISTRATION — everything below was fixed by earlier experiments, before
this file was written, and nothing here is chosen with reference to test data:

  timeframe / horizon   H1, 8 bars            fixed in R02 on economic grounds
  model                 logit_l2_C0.1         fixed in R06 as the linear
                                              representative, used in R10
  position rule         deadband 0.0,         fixed in R05's grid, used for
                        overlapping book      the walk-forward arms
  protocol              expanding-window walk-forward, min 12,000 training
                        bars, 1,500 bars per fold, labels purged by 8 bars at
                        every window edge, refit before every fold
  comparators           always_long, always_short, coin_flip
  cost                  turnover x spread / 2, plus a sensitivity sweep

No configuration is selected, tuned, or filtered using the test data. The
walk-forward simply continues across the validation/test boundary, so every
test fold is traded by a model that saw only strictly earlier bars.

Why run this at all when nothing survived validation? Because a negative
confirmed on genuinely untouched data is a far stronger claim than a negative
confirmed on data that has been looked at repeatedly. This is a confirmatory
run, not a search. Its outcome cannot change any decision — nothing is being
promoted — but it is the honest close to the study.

**After this run, the test split is spent.** Any future work on XAUUSD needs a
new held-out period.

Run:  python -m pureml.research.r11_final_test
"""
from __future__ import annotations

import json
import os
import warnings
from datetime import datetime, timezone

import numpy as np

from ..config import (ARTIFACT_DIR, SPLIT_TEST, SPLIT_TRAIN, SPLIT_VALID,
                      SYMBOL)
from ..data.dataset import build_dataset, nonoverlap_mask
from ..models.fit import Preprocessor, build_model, positions_from_proba
from .evaluate import HEADER, evaluate_positions, format_row

TIMEFRAME, HORIZON = "H1", 8
MODEL = ("logit_l2_C0.1", {"kind": "logit", "penalty": "l2", "C": 0.1})
RULE = {"deadband": 0.0, "hold": 8}
MIN_TRAIN, STEP = 12_000, 1_500
SEED = 20260828
COST_MULTIPLIERS = (0.0, 0.5, 1.0, 2.0)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def log(s):
    print(s, flush=True)


def main():
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r11_final_test_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("=" * 96)
    log("R11 — FINAL TEST EVALUATION  (%s %s, horizon %d)"
        % (SYMBOL, TIMEFRAME, HORIZON))
    log("=" * 96)
    log("PRE-REGISTERED, run once, no selection performed on test data.")
    log("  model         %s" % MODEL[0])
    log("  rule          deadband %.2f, overlapping book of %d"
        % (RULE["deadband"], RULE["hold"]))
    log("  protocol      expanding walk-forward, min train %s, step %s,"
        % (f"{MIN_TRAIN:,}", f"{STEP:,}"))
    log("                labels purged %d bars at every window edge" % HORIZON)
    log("  comparators   always_long, always_short, coin_flip")
    log("")

    ds = build_dataset(TIMEFRAME, HORIZON)
    nov = nonoverlap_mask(ds)
    X, y = ds.X, ds.y_up
    n = len(ds)
    name, spec = MODEL

    # Walk forward across the WHOLE history. Test folds are traded by models
    # fitted only on strictly earlier bars.
    pos = np.zeros(n)
    oos = np.zeros(n, dtype=bool)
    idx = np.arange(n)
    for s in range(MIN_TRAIN, n - STEP + 1, STEP):
        tr = idx[:max(0, s - HORIZON)]
        fold = idx[s:s + STEP]
        warm = idx[max(0, s - HORIZON):s + STEP]
        pre = Preprocessor.fit(X[tr])
        clf = build_model(spec, SEED)
        clf.fit(pre.transform(X[tr]), y[tr])
        pr = clf.predict_proba(pre.transform(X[warm]))[:, 1]
        pos[fold] = positions_from_proba(pr, **RULE)[-len(fold):]
        oos[fold] = True

    mtest = ds.mask(SPLIT_TEST) & oos
    t0 = datetime.fromtimestamp(ds.time[mtest][0] / 1000, tz=timezone.utc)
    t1 = datetime.fromtimestamp(ds.time[mtest][-1] / 1000, tz=timezone.utc)
    log("TEST PERIOD  %s -> %s   %s bars   buy&hold %+.1f $/oz"
        % (t0.date(), t1.date(), f"{int(mtest.sum()):,}",
           float(ds.close[mtest][-1] - ds.close[mtest][0])))
    log("")

    rng = np.random.default_rng(SEED)
    strategies = {
        name: pos,
        "always_long": np.ones(n),
        "always_short": -np.ones(n),
        "coin_flip": rng.choice([-1.0, 1.0], size=n),
    }

    log("=" * 96)
    log("RESULT ON THE UNTOUCHED TEST SPLIT")
    log("=" * 96)
    log(HEADER)
    res = {}
    for k, p in strategies.items():
        r = evaluate_positions(p, ds, mtest, nov)
        res[k] = r
        log(format_row(k, r))
    log("")

    # deterioration: same model, same protocol, on validation
    mval = ds.mask(SPLIT_VALID) & oos
    rv = evaluate_positions(pos, ds, mval, nov)
    log("=" * 96)
    log("OUT-OF-SAMPLE DETERIORATION")
    log("=" * 96)
    log("  %-14s %11s %11s %9s %9s" % ("split", "net", "gross", "acc",
                                       "drift"))
    for lbl, r in (("validation", rv), ("test", res[name])):
        log("  %-14s %11.1f %11.1f %9.4f %9.4f"
            % (lbl, r["total_net"], r["gross_total"], r["accuracy"],
               r["drift_base_rate"]))
    log("")

    log("=" * 96)
    log("COST SENSITIVITY ON TEST")
    log("=" * 96)
    log("  %-14s %12s %12s" % ("cost x", "model net", "always_long"))
    cs = {}
    for cm in COST_MULTIPLIERS:
        r = evaluate_positions(pos, ds, mtest, nov, cost_multiplier=cm)
        ra = evaluate_positions(np.ones(n), ds, mtest, nov,
                                cost_multiplier=cm)
        cs[cm] = {"model_net": r["total_net"], "long_net": ra["total_net"]}
        log("  %-14s %12.1f %12.1f"
            % ("%.1fx spread" % cm, r["total_net"], ra["total_net"]))
    log("")

    yrs = np.array([datetime.fromtimestamp(t / 1000, tz=timezone.utc).year
                    for t in ds.time])
    log("=" * 96)
    log("TEST PERFORMANCE BY YEAR")
    log("=" * 96)
    log("  %-6s %9s %12s %12s %10s" % ("year", "bars", "model net",
                                       "always_long", "model acc"))
    by_year = {}
    for yr in sorted(set(yrs[mtest])):
        m = mtest & (yrs == yr)
        if m.sum() < 100:
            continue
        r = evaluate_positions(pos, ds, m, nov)
        ra = evaluate_positions(np.ones(n), ds, m, nov)
        by_year[int(yr)] = {"net": r["total_net"], "long": ra["total_net"],
                            "acc": r["accuracy"], "n": int(m.sum())}
        log("  %-6d %9s %12.1f %12.1f %10.4f"
            % (yr, f"{int(m.sum()):,}", r["total_net"], ra["total_net"],
               r["accuracy"]))
    log("")

    log("=" * 96)
    log("FINAL VERDICT")
    log("=" * 96)
    m, a = res[name], res["always_long"]
    log("  model net on test          %+.1f" % m["total_net"])
    log("  model gross on test        %+.1f" % m["gross_total"])
    log("  always_long net on test    %+.1f" % a["total_net"])
    log("  model accuracy             %.4f  (drift base rate %.4f)"
        % (m["accuracy"], m["drift_base_rate"]))
    log("  model t(ind)               %+.2f" % m["t_independent"])
    log("")
    if m["total_net"] > 0 and m["total_net"] > a["total_net"] \
            and m["t_independent"] > 2.0:
        log("  The model is profitable and beats drift on untouched data.")
    else:
        log("  PURE ML FAILED TO FIND A ROBUST OUT-OF-SAMPLE EDGE.")
        log("")
        log("  This confirms on genuinely untouched data what R05 through R10")
        log("  established on validation. It is a successful research result:")
        log("  the question was answered, and the answer is no.")
    log("")
    log("  The test split is now spent. Any further XAUUSD research needs a")
    log("  new held-out period.")
    log("")

    with open(os.path.join(out_dir, "final_test.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "timeframe": TIMEFRAME,
                   "horizon": HORIZON, "generated": stamp, "model": name,
                   "rule": RULE, "min_train": MIN_TRAIN, "step": STEP,
                   "test_bars": int(mtest.sum()),
                   "results": res, "validation_same_model": rv,
                   "cost_sensitivity": {str(k): v for k, v in cs.items()},
                   "by_year": by_year}, fh, indent=2, default=float)
    log("written: %s" % out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
