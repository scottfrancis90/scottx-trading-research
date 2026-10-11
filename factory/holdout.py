# Author: Scott (ScottX Research)
"""The holdout. One test, one prediction, then the split is spent.

WHY THIS FILE IS DEFENSIVE TO THE POINT OF BEING AWKWARD
  The gold project's H1 test split was spent by running "just one more check"
  against it. Once that happens there is no way to un-see it, and every later
  number on that split is contaminated. So this file does not trust the
  caller -- not even me:

  * A LOCK FILE per strategy family. Running twice on the same family is
    refused, and the refusal names the date of the first run.
  * A PRE-REGISTRATION with a sha, frozen BEFORE the data is touched. If the
    genome or the prediction changes afterwards, the sha changes and the
    result is recorded as invalid.
  * A HUMAN REASON, supplied by a person, for why the rule should work. "The
    GA found it" is rejected by a literal string check. A mechanism that
    cannot be stated is a mechanism that cannot be trusted.
  * THE RESULT IS WRITTEN WHETHER IT PASSES OR FAILS. A holdout you only
    record when it passes is not a holdout.

  There is no flag to bypass any of this. If a holdout needs re-running, the
  lock file has to be deleted by hand, deliberately, and that act is visible
  in the repository.
"""
import hashlib
import json
import os
import time

from factory import data
from factory import evaluate as E
from factory import genome as G
from factory.config import LOCKS
from factory.simulate import metrics

BANNED_REASONS = ("the ga found it", "ga found it", "it works", "the numbers",
                  "backtest", "it passed", "because it passed", "dunno", "not sure")


def family_id(g):
    """what counts as 'the same family' for the purposes of the lock.

    Deliberately the SKELETON, not the full genome: re-running the holdout
    with one parameter nudged is exactly the abuse this is preventing.
    """
    sk = G.skeleton(g)
    sk["tf"] = g["tf"]
    return hashlib.sha1(json.dumps(sk, sort_keys=True).encode()).hexdigest()[:16]


def lock_path(g):
    return os.path.join(LOCKS, "holdout_%s.json" % family_id(g))


def is_spent(g):
    p = lock_path(g)
    if not os.path.exists(p):
        return False, None
    return True, json.load(open(p, encoding="utf-8"))


def run(g, reason, prediction, ledger_size, validate_metrics, force_note=None):
    """the one shot.

    reason:     a person's answer to "why would this work?"
    prediction: dict with at least mean_lo, mean_hi, and what counts as failure
    """
    spent, prev = is_spent(g)
    if spent:
        return dict(ok=False, error="ALREADY SPENT",
                    detail="this family's holdout was run on %s and cannot be run again. "
                           "Delete %s by hand if that is genuinely intended."
                           % (prev.get("when"), lock_path(g)))

    r = (reason or "").strip().lower()
    if len(r) < 25 or any(b in r for b in BANNED_REASONS):
        return dict(ok=False, error="NO MECHANISM",
                    detail="A reason the rule should work is required, in plain words, "
                           "and it must not be a restatement of the backtest. Got: %r" % reason)

    frozen = dict(genome=g, reason=reason, prediction=prediction,
                  ledger_size=int(ledger_size),
                  validate=dict(n=validate_metrics["n"], mean=validate_metrics["mean"],
                                t=validate_metrics["t"]),
                  frozen_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
    sha = hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest()[:16]

    # ---- the only place the holdout is ever read
    df = data.split(g["tf"], "holdout")
    sp = data.spread_price(g["tf"], "train")      # costs from TRAIN, never holdout
    res = E.run(g, "holdout")
    m = metrics(res["R"]) if (res is not None and len(res)) else None

    verdict = "NO TRADES"
    if m is not None:
        lo, hi = prediction["mean_lo"], prediction["mean_hi"]
        inband = lo <= m["mean"] <= hi
        failed = (m["mean"] < prediction.get("fail_below", 0.0)
                  or m["m1"] <= 0 or m["m2"] <= 0)
        verdict = "FAILED" if failed else ("PASSED" if inband else "PASSED (outside the predicted band)")

    out = dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), sha=sha, family=family_id(g),
               genome=g, reason=reason, prediction=prediction,
               ledger_size=int(ledger_size), verdict=verdict,
               holdout=(dict(n=m["n"], mean=m["mean"], t=m["t"], win=m["win"],
                             m1=m["m1"], m2=m["m2"], total=m["total"], rdd=m["rdd"])
                        if m else None),
               note=force_note)
    os.makedirs(LOCKS, exist_ok=True)
    with open(lock_path(g), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    out["ok"] = True
    return out


def show(res):
    if not res.get("ok"):
        print("  HOLDOUT REFUSED: %s" % res["error"])
        print("    %s" % res["detail"])
        return
    print("  HOLDOUT RUN — family %s, sha %s" % (res["family"], res["sha"]))
    print("    reason given: %s" % res["reason"])
    p = res["prediction"]
    print("    predicted mean R between %+0.3f and %+0.3f; failure below %+0.3f" % (
        p["mean_lo"], p["mean_hi"], p.get("fail_below", 0.0)))
    h = res["holdout"]
    if h:
        print("    measured: n=%d  mean %+0.4f  t %+0.2f  win %.1f%%  halves %+0.4f/%+0.4f" % (
            h["n"], h["mean"], h["t"], 100 * h["win"], h["m1"], h["m2"]))
    print("    VERDICT: %s" % res["verdict"])
    print("    written to %s — this family's holdout is now spent." % lock_path(res["genome"]))
