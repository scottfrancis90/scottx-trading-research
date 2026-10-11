# Author: Scott (ScottX Research)
"""Fitness, and the ledger that is the denominator for everything after it.

FITNESS IS COMPUTED ON TRAIN ONLY. The validation split is not visible to the
GA in any form -- not for early stopping, not for tie-breaking, not for
"just checking". That is refused by design in ARCHITECTURE.md and it is
refused here by the fact that no function in this file can reach it.

WHAT THE SHAPE OF THIS FUNCTION IS FOR
  A GA maximises whatever you give it, including the parts you did not mean.
  Given plain mean R it will find the single luckiest cell in the grid, on a
  hundred trades, with five genes. So:

    - trades below MIN_TRADES are a hard fail, not a penalty
    - below SOFT_TRADES costs fitness
    - a genome whose two TRAIN halves disagree is penalised: a rule that only
      worked in 2013 is not a rule
    - genes past the third cost fitness, so a simpler genome wins ties
    - a PEAK is penalised. If a genome's one-grid-step neighbours collapse,
      it sits on a spike in the search surface and will not survive contact
      with the validation split. Plateaus are what generalise.

THE LEDGER
  Every genome ever EVALUATED is appended, deduplicated by fingerprint. This
  is the number Bonferroni divides by. It lives on disk and survives across
  runs, because the multiple-testing burden is cumulative: a second run on
  the same data does not get a fresh alpha.
"""
import json
import os
import threading

import numpy as np

from factory import evaluate as E
from factory import genome as G
from factory.config import (GENE_PENALTY_FROM, LEDGER, MIN_TRADES, SOFT_TRADES)
from factory.simulate import metrics

HARD_FAIL = -99.0
_lock = threading.Lock()


def _norm_ppf(p):
    """inverse standard normal CDF, Acklam's approximation. No scipy."""
    if not (0.0 < p < 1.0):
        return float("nan")
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00)
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = np.sqrt(-2 * np.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > ph:
        q = np.sqrt(-2 * np.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q /            (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


class Ledger:
    """append-only, deduplicated, survives runs"""

    def __init__(self, path=LEDGER):
        self.path = path
        self.seen = set()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for ln in f:
                    try:
                        self.seen.add(json.loads(ln)["fp"])
                    except Exception:
                        pass

    def __len__(self):
        return len(self.seen)

    def record(self, g, m, fit, run_tag):
        fp = G.fingerprint(g)
        if fp in self.seen:
            return False
        self.seen.add(fp)
        row = dict(fp=fp, run=run_tag, fitness=round(float(fit), 6),
                   tf=g["tf"], mech=g["mechanism"], desc=G.describe(g),
                   n=(m or {}).get("n"), mean=(m or {}).get("mean"),
                   t=(m or {}).get("t"), m1=(m or {}).get("m1"), m2=(m or {}).get("m2"))
        with _lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
        return True

    def search_burden(self):
        """the honest denominator: distinct genomes x the number of ledger resets.

        The ledger has been reset four times, each for a real defect -- drifting
        indicator definitions, row-count timeframes, a missing minimum R, and
        controls that scored a different sample than the rule. Every one of
        those runs was still a search over this same data. Throwing away the
        RECORD of a search does not undo the search. So the multiple-testing
        burden is cumulative across resets and the alpha is divided by all of
        it. `reset_history.json` lists them.
        """
        mult = 1
        try:
            import json as _j
            mult = max(1, _j.load(open(os.path.join(os.path.dirname(self.path),
                       "reset_history.json"), encoding="utf-8"))["multiplier"])
        except Exception:
            pass
        return max(len(self.seen), 1) * mult

    def bonferroni_t(self, alpha=0.05):
        """the |t| a candidate must clear on VALIDATION, given how much was tried.

        Two-sided, normal approximation. With 10,000 genomes this is about 4.6.

        scipy is not required: the inverse normal CDF is Acklam's rational
        approximation, accurate to about 1.15e-9 -- far beyond what a
        significance threshold needs.
        """
        n = self.search_burden()
        return float(abs(_norm_ppf(alpha / (2.0 * n))))


def plateau_score(g, slices=None, spreads=None, cache=None):
    """fraction of one-grid-step neighbours that are still positive on TRAIN.

    A genome on a spike has few positive neighbours; a genome on a plateau has
    many. This is the single most useful guard a GA can have, because a spike
    is exactly what a search finds when there is nothing there.
    """
    nb = G.neighbours(g)
    if not nb:
        return 1.0, 0
    good = 0
    used = 0
    for h in nb[:6]:                       # 6 is enough to see a cliff; 12 doubled the run time
        m = _train_metrics(h, slices, spreads, cache)
        if m is None:
            continue
        used += 1
        if m["mean"] > 0:
            good += 1
    return (good / used if used else 1.0), used


def outlier_dominated(R, share=0.40):
    """True when the single best trade carries more than `share` of the total.

    A result that rests on one trade is not a result. This is the guard that
    would have caught the +584 R artifact without needing to know its cause.
    """
    R = np.asarray(R, float)
    tot = R.sum()
    if len(R) < 20 or tot <= 0:
        return False
    return (R.max() / tot) > share


def book(g, which, sym=None):
    """one genome's trades on one split, POOLED across symbols on FX.

    On gold this is a single series and nothing changes. On FX a genome is
    evaluated on every pair and the returns are concatenated, because the
    cross-section IS the test: a real edge shows on most pairs, noise shows on
    one or two. `pairs_pos` and `pairs` are carried alongside so a gate can ask
    how many pairs it worked on, which is much harder to fake than a pooled t.

    Pairs are NOT dropped for having few trades -- that would select on sample
    size, which correlates with volatility and therefore with the answer.
    """
    from factory import market as MK
    syms = [sym] if sym else list(MK.symbols())
    Rs, pos, used = [], 0, 0
    for s_ in syms:
        try:
            r = E.run(g, which, sym=s_)
        except Exception:
            r = None
        if r is None or not len(r):
            continue
        arr = r["R"].to_numpy()
        Rs.append(arr)
        used += 1
        pos += arr.mean() > 0
    if not Rs:
        return None, 0, 0
    return np.concatenate(Rs), pos, used


def _train_metrics(g, slices=None, spreads=None, cache=None):
    fp = G.fingerprint(g)
    if cache is not None and fp in cache:
        return cache[fp]
    R, pos, used = book(g, "train")
    m = metrics(R) if R is not None and len(R) else None
    if m is not None:
        m = dict(m, pairs_pos=pos, pairs=used)
        if outlier_dominated(R):
            m = dict(m, outlier=True)
    if cache is not None:
        cache[fp] = m
    return m


def fitness(g, slices=None, spreads=None, cache=None, with_plateau=True):
    """(fitness, train metrics). TRAIN only."""
    m = _train_metrics(g, slices, spreads, cache)
    floor = MIN_TRADES
    if m is None or m["n"] < floor:
        return HARD_FAIL, m
    if m.get("outlier"):
        return HARD_FAIL, m      # one trade carried it; that is not a result
    # FITNESS IS A LOWER CONFIDENCE BOUND, not a mean.
    #
    # A flat small-sample penalty does not work: a genome with mean +0.70 on
    # 161 trades absorbs -0.05 and still beats a genome with +0.39 on 633
    # trades and a HIGHER t-stat. So the GA maximised luck. Subtracting two
    # standard errors makes the penalty proportional to the uncertainty,
    # which is the thing that actually differs between those two genomes.
    se = abs(m["mean"] / m["t"]) if m.get("t") else 1.0
    f = m["mean"] - 2.0 * se
    if m["n"] < SOFT_TRADES:
        f -= 0.05
    if m["m1"] <= 0 or m["m2"] <= 0:
        f -= 0.03
    extra = G.n_active(g) - GENE_PENALTY_FROM
    if extra > 0:
        f -= 0.02 * extra
    # The plateau test costs six extra simulations, so it is only spent on
    # genomes that are still alive after everything else. A genome that is
    # already losing does not need to be told it is also on a spike.
    if with_plateau and f > 0:
        frac, used = plateau_score(g, slices, spreads, cache)
        if used >= 4 and frac < 0.8:
            f -= 0.05 * (0.8 - frac) / 0.8
    return f, m
