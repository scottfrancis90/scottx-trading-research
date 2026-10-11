# Author: Scott (ScottX Research)
"""R02 — target and horizon research. No model is fitted here.

Two questions, both answerable without machine learning, and both decisive
for what follows.

1. ECONOMIC REQUIREMENT
   For a directional trade held k bars, with expected absolute move M_k and
   round-trip cost s, expectancy per trade is

       E = (2p - 1) * M_k - s

   so break-even directional accuracy is

       p* = 0.5 + s / (2 * M_k)

   This is the bar any classifier must clear. It falls as the horizon
   lengthens (M_k grows) and rises as the timeframe shortens. Computed from
   REALISED moves, not a sqrt-scaling assumption.

2. IS THERE ANY STRUCTURE?
   Model-free screens, so a null result cannot be blamed on a bad model:
     * Lo-MacKinlay variance ratio at several horizons. VR = 1 under a
       random walk; the z-statistic is heteroskedasticity-robust.
     * Sign persistence — P(next return same sign as last).
     * Directional drift — P(k-bar return > 0).

DRIFT IS A TRAP AND IS REPORTED SEPARATELY
Gold rose from ~1200 to ~2500 across this sample. A model that learns
"always long" will look skilful while carrying no information. Every
directional figure here is reported against the buy-and-hold base rate, not
against 50%.

Overlapping horizons inflate apparent significance, so the count of
NON-OVERLAPPING samples is reported alongside every cell.

Run:  python -m pureml.research.r02_target_research
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone

import numpy as np

from ..config import (ARTIFACT_DIR, DATA_START, SPLIT_TRAIN, SYMBOL,
                      split_of)
from ..data.loader import aggregate, load_raw

TIMEFRAMES = ["M15", "M30", "H1", "H4"]
HORIZONS = [1, 2, 4, 8, 16, 32, 64]
VR_LAGS = [2, 4, 8, 16, 32]


def log(s):
    print(s, flush=True)


def variance_ratio(r, q):
    """Lo-MacKinlay variance ratio with a heteroskedasticity-robust z.

    Returns (VR, z). VR = 1 under a random walk.
    """
    r = r[~np.isnan(r)]
    n = len(r)
    if n < q * 4:
        return float("nan"), float("nan")
    mu = r.mean()
    var1 = np.sum((r - mu) ** 2) / (n - 1)
    if var1 <= 0:
        return float("nan"), float("nan")
    rq = np.convolve(r, np.ones(q), mode="valid")          # q-period sums
    m = n - q + 1
    varq = np.sum((rq - q * mu) ** 2) / (m * q)
    vr = varq / var1
    # Heteroskedasticity-robust variance (Lo & MacKinlay 1988).
    #   delta_j = sum (r_t-mu)^2 (r_{t-j}-mu)^2 / [sum (r_t-mu)^2]^2
    #   theta   = sum_j [2(q-j)/q]^2 delta_j
    #   z       = (VR - 1) / sqrt(theta)
    # delta_j already carries the 1/n scaling through the squared
    # denominator, so multiplying by n here understates z by sqrt(n).
    denom = np.sum((r - mu) ** 2) ** 2
    theta = 0.0
    for j in range(1, q):
        d = r[j:] - mu
        e = r[:-j] - mu
        delta = np.sum((d ** 2) * (e ** 2)) / denom
        theta += ((2.0 * (q - j) / q) ** 2) * delta
    z = (vr - 1.0) / math.sqrt(theta) if theta > 0 else float("nan")
    return float(vr), float(z)


def main():
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = os.path.join(ARTIFACT_DIR, "r02_targets_%s" % stamp)
    os.makedirs(out_dir, exist_ok=True)

    log("R02 — TARGET AND HORIZON RESEARCH  (%s)" % SYMBOL)
    log("No model is fitted. Establishing the economic bar and screening")
    log("for any structure at all.")
    log("")

    base = load_raw("M1").slice_from(DATA_START)
    log("post-hole M1 bars: %s" % f"{len(base):,}")

    # ---- drift: the baseline every directional result must beat ----
    log("")
    log("=" * 96)
    log("DRIFT BASELINE — what 'always long' achieves for free")
    log("=" * 96)
    tr_mask = np.array([split_of(int(t)) == SPLIT_TRAIN for t in base.time])
    c_tr = base.close[tr_mask]
    log("  train period: %.2f -> %.2f  (%+.1f%% buy-and-hold)"
        % (c_tr[0], c_tr[-1], 100.0 * (c_tr[-1] / c_tr[0] - 1.0)))
    log("  Any directional accuracy must be read against the base rate of")
    log("  positive returns below, never against 50%.")
    log("")

    results = {}
    for tf in TIMEFRAMES:
        b = base if tf == "M1" else aggregate(base, tf)
        keep = np.array([split_of(int(t)) == SPLIT_TRAIN for t in b.time])
        c = b.close[keep]
        sp = b.spread[keep]
        n = len(c)
        if n < 500:
            continue
        logc = np.log(c)
        r1 = np.diff(logc)
        med_spread = float(np.median(sp))

        log("=" * 96)
        log("%s — %s train bars   median spread %.3f" % (tf, f"{n:,}",
                                                         med_spread))
        log("=" * 96)
        log("  %-4s %12s %10s %10s %12s %11s"
            % ("k", "E|move| $", "P(up)", "req. acc", "edge needed",
               "non-overlap"))
        cells = {}
        for k in HORIZONS:
            if n <= k + 10:
                continue
            fwd = logc[k:] - logc[:-k]
            price = c[:-k]
            move = np.abs(np.expm1(fwd)) * price          # $ move over k bars
            em = float(np.mean(move))
            p_up = float(np.mean(fwd > 0))
            req = 0.5 + med_spread / (2.0 * em) if em > 0 else float("inf")
            # how much better than the drift base rate is required
            edge_needed = req - max(p_up, 1.0 - p_up)
            n_ind = (n - k) // k
            cells[str(k)] = {"E_abs_move": em, "p_up": p_up,
                             "required_accuracy": req,
                             "edge_over_drift": edge_needed,
                             "independent_samples": int(n_ind)}
            log("  %-4d %12.4f %10.4f %10.4f %12.4f %11s"
                % (k, em, p_up, req, edge_needed, f"{n_ind:,}"))

        log("")
        log("  variance ratio (VR=1 is a random walk):")
        vrs = {}
        for q in VR_LAGS:
            vr, z = variance_ratio(r1, q)
            vrs[str(q)] = {"vr": vr, "z": z}
            flag = ""
            if not math.isnan(z) and abs(z) > 1.96:
                flag = "   <-- rejects random walk"
            log("     q=%-3d VR=%.4f  z=%+.2f%s" % (q, vr, z, flag))
        sgn = np.sign(r1)
        ok = sgn != 0
        persist = float(np.mean(sgn[:-1][ok[:-1] & ok[1:]]
                                == sgn[1:][ok[:-1] & ok[1:]]))
        log("     sign persistence P(same sign as previous) = %.4f" % persist)
        log("")
        results[tf] = {"train_bars": n, "median_spread": med_spread,
                       "horizons": cells, "variance_ratio": vrs,
                       "sign_persistence": persist}

    # ---- viability shortlist ----
    log("=" * 96)
    log("VIABILITY SHORTLIST")
    log("=" * 96)
    log("Cells needing < 5 accuracy points over the drift base rate, with")
    log(">= 1,000 non-overlapping training samples:")
    short = []
    for tf, d in results.items():
        for k, cell in d["horizons"].items():
            if (cell["edge_over_drift"] < 0.05
                    and cell["independent_samples"] >= 1000):
                short.append((tf, int(k), cell))
    if not short:
        log("  NONE — no timeframe/horizon combination is reachable.")
    for tf, k, cell in sorted(short, key=lambda x: x[2]["edge_over_drift"]):
        log("  %-4s k=%-3d  req acc %.4f  vs drift %.4f  ->  needs %+.4f"
            "   (%s independent samples)"
            % (tf, k, cell["required_accuracy"], cell["p_up"],
               cell["edge_over_drift"], f"{cell['independent_samples']:,}"))

    with open(os.path.join(out_dir, "targets.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"symbol": SYMBOL, "generated": stamp,
                   "results": results,
                   "shortlist": [{"tf": a, "k": b, **c} for a, b, c in short]},
                  fh, indent=2)
    log("")
    log("written: %s" % os.path.join(out_dir, "targets.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
