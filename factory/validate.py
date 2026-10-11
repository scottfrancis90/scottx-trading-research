# Author: Scott (ScottX Research)
"""The gates. A TRAIN winner is a hypothesis; this is where it is tested.

ARCHITECTURE.md lists eight gates and says "all of these, or dead". They are
implemented here in the order that kills fastest and cheapest.

  1  ENOUGH TRADES on validation at all
  2  BOTH HALVES of validation positive
  3  BONFERRONI over the whole ledger -- the denominator is every distinct
     genome ever evaluated, across runs, not just this one
  4  INVERTED control: the same trades the other way must lose, and must lose
     by more than CONTROL_MARGIN
  5  SHUFFLED control: the same signal TIMES with the direction randomised
     must come out at about minus the cost. If it does not, the geometry is
     doing the work, not the rule
  6  WINDOW-SHIFT control, for session genes only: shifting the window must
     make it worse. Finding 51 Q3 killed an entire family with this
  7  PLATEAU on validation, not just train
  8  The collapse guard: COLLAPSE / IMPROVEMENT / DISCOVERY against what this
     project already knows

Expect zero survivors on most runs. That is the design working, not failing.
"""
import numpy as np
import pandas as pd

from factory import data
from factory import evaluate as E
from factory import genome as G
from factory.config import (CONTROL_MARGIN, MIN_R_SPREADS, PLATEAU_MIN_POSITIVE,
                            TIMEFRAMES)
from factory.simulate import AT_PRICE, metrics, walk


def _run(g, which, sym=None):
    """the genome's trades, POOLED across symbols when the market is FX."""
    from factory import market as MK
    syms = [sym] if sym else list(MK.symbols())
    out = []
    for s_ in syms:
        try:
            r = E.run(g, which, sym=s_)
        except Exception:
            r = None
        if r is not None and len(r):
            out.append(r)
    if not out:
        return None
    return pd.concat(out, ignore_index=True) if len(out) > 1 else out[0]


def pairs_positive(g, which):
    """(pairs with a positive mean, pairs that traded at all).

    The cross-section is the defence gold never had. A rule with a real edge
    works on most pairs; noise works on one or two and scatters on the rest.
    This is far harder to fake than a pooled t-statistic, because pooling can
    be carried by a single pair with many trades.
    """
    from factory import market as MK
    pos = used = 0
    win = []
    for s_ in MK.symbols():
        r = _run(g, which, sym=s_)
        if r is None:
            continue
        used += 1
        if float(r["R"].mean()) > 0:
            pos += 1
            win.append(s_)
    return pos, used, win


def _arrays(g, which):
    """the full series plus this split's range, so indicators match everywhere"""
    tf = g["tf"]
    df = data.load(tf)
    i0, i1 = data.index_range(tf, which)
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    return df["time"], o, h, l, c, i0, i1, data.spread_price(tf, "train")


def _mirror_book(g, which, flip):
    """the rule's OWN trades, re-run with the direction changed.

    `flip(side, rng)` returns the direction to take. Identical fill bars,
    identical fill prices, identical R and identical reward distance -- the
    only thing that differs is which way the trade points. Anything else and
    the control is scoring a different sample, which is how the previous
    version of this file produced a "shuffled control beats the rule".
    """
    from factory import market as MK
    if len(MK.symbols()) > 1:
        out = [_mirror_one(g, which, flip, s_) for s_ in MK.symbols()]
        out = [x for x in out if x is not None and len(x)]
        return pd.concat(out, ignore_index=True) if out else None
    return _mirror_one(g, which, flip, None)


def _mirror_one(g, which, flip, sym):
    base = _run(g, which, sym=sym)
    if base is None or not len(base):
        return None
    tf = g["tf"]
    df = data.load(tf, sym)
    i0, i1 = data.index_range(tf, which, sym)
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    sp = data.spread_price(tf, "train", sym)
    rng = np.random.default_rng(0)
    sigs = []
    for _, r in base.iterrows():
        side = flip(int(r["side"]), rng)
        e = float(r["entry"])
        # DEFECT 16 (2026-10-08): "stop" is the FINAL stop, moved by a partial
        # or a trail, so rebuilding R from it shrank R and inflated the mirror
        # (+0.50 R on a rule whose true mirror was ~0). Use the initial stop.
        R = abs(e - float(r["stop0"] if "stop0" in r and np.isfinite(r["stop0"]) else r["stop"]))
        dist = abs(float(r["target"]) - e)
        sigs.append(dict(bar=int(r["fill_bar"]), side=side, mode=AT_PRICE, entry=e,
                         stop=e - side * R, target=e + side * dist))
    # the mirror is managed exactly like the rule, or it is a different trade
    mg = g.get("manage", {"gene": "plain"})
    part = mg.get("at") if mg["gene"] in ("partial", "both") else None
    trail = mg.get("k") if mg["gene"] in ("trail", "both") else None
    from factory.simulate import atr as _atr
    A = _atr(h, l, c) if trail else None
    return walk(o, h, l, c, sp, sigs, E.timeout_bars(g), one_at_a_time=False,
                end_cap=i1, min_r_spreads=MIN_R_SPREADS, partial_at=part,
                trail_atr=trail, atr_arr=A)


def inverted(g, which):
    return _mirror_book(g, which, lambda s, rng: -s)


def shuffled(g, which, seed=0):
    """the same trades with the direction decided by a coin.

    If this makes money, the money is in the geometry and the timing, not in
    the direction the rule picks -- and a rule that does not pick a direction
    is not a rule.
    """
    return _mirror_book(g, which, lambda s, rng: 1 if rng.random() < 0.5 else -1)


def window_shift(g):
    """session genes only: move the window and it must get worse"""
    shifted = []
    for slot in ("context", "filter"):
        if g[slot]["gene"] in ("session_range", "hour_window"):
            for delta in (-4, +4):
                h = {k: (dict(v) if isinstance(v, dict) else v) for k, v in g.items()}
                h[slot] = dict(g[slot])
                h[slot]["start"] = (h[slot]["start"] + delta) % 24
                h[slot]["end"] = (h[slot]["end"] + delta) % 24
                if h[slot]["start"] < h[slot]["end"]:
                    shifted.append(h)
    return shifted


def plateau_on(g, which, limit=10):
    nb = G.neighbours(g)[:limit]
    good = used = 0
    for h in nb:
        r = _run(h, which)
        m = metrics(r["R"]) if r is not None else None
        if m is None:
            continue
        used += 1
        good += (m["mean"] > 0)
    return (good / used if used else 1.0), used


def known_on_validation(which="validate"):
    """the known families' own numbers on VALIDATION, so IMPROVEMENT can be
       judged against a real number rather than a remembered one.
       The probes are listed in genome.KNOWN_PROBES."""
    out = {}
    for name, g in G.KNOWN_PROBES.items():
        r = _run(g, which)
        out[name] = metrics(r["R"]) if r is not None else None
    return out


def gate(g, ledger, which, known):
    """run every gate. Returns (passed, rows) where rows explain each one."""
    rows = []
    r = _run(g, which)
    m = metrics(r["R"]) if r is not None else None
    if m is None or m["n"] < 60:
        rows.append(("trades on validation", "n=%s" % (m["n"] if m else 0), False))
        return False, rows, m
    rows.append(("trades on validation", "n=%d" % m["n"], True))

    ok_half = m["m1"] > 0 and m["m2"] > 0
    rows.append(("both halves positive", "%+.4f / %+.4f" % (m["m1"], m["m2"]), ok_half))

    need = ledger.bonferroni_t()
    ok_t = abs(m["t"]) >= need and m["mean"] > 0
    rows.append(("Bonferroni over %s (%s x %d resets)" % (
                     "{:,}".format(ledger.search_burden()), "{:,}".format(len(ledger)),
                     max(1, ledger.search_burden() // max(len(ledger), 1))),
                 "t %+.2f, need |t| >= %.2f" % (m["t"], need), ok_t))

    inv = inverted(g, which)
    mi = metrics(inv["R"]) if len(inv) else None
    ok_inv = mi is not None and (m["mean"] - mi["mean"]) > CONTROL_MARGIN and mi["mean"] <= 0
    rows.append(("inverted control loses",
                 "mirror %+.4f, edge %+.4f" % (mi["mean"] if mi else float("nan"),
                                               (m["mean"] - mi["mean"]) if mi else float("nan")), ok_inv))

    sh = shuffled(g, which)
    ms = metrics(sh["R"]) if len(sh) else None
    ok_sh = ms is None or ms["mean"] < 0.02
    rows.append(("shuffled direction is flat",
                 "%+.4f" % (ms["mean"] if ms else float("nan")), ok_sh))

    shifts = window_shift(g)
    if shifts:
        worse = 0
        for h in shifts:
            rr = _run(h, which)
            mm = metrics(rr["R"]) if rr is not None else None
            if mm is None or mm["mean"] < m["mean"]:
                worse += 1
        ok_ws = worse == len(shifts)
        rows.append(("window shift is worse", "%d of %d shifts worse" % (worse, len(shifts)), ok_ws))
    else:
        ok_ws = True

    frac, used = plateau_on(g, which)
    ok_pl = used < 4 or frac >= PLATEAU_MIN_POSITIVE
    rows.append(("plateau on validation", "%.0f%% of %d neighbours positive" % (100 * frac, used), ok_pl))

    from factory import market as MK
    if len(MK.symbols()) > 1:
        pp, pu, win = pairs_positive(g, which)
        eff = MK.effective_independent(win)
        # 17 pairs carry only 5.3 independent bets, so counting rows would let
        # one currency move satisfy the gate six times over. 3.0 effective is
        # a clear majority of the 5.3 that actually exist.
        ok_pairs = pu >= 8 and eff >= 3.0
        rows.append(("independent pairs positive (need 3.0)",
                     "%d of %d pairs = %.1f independent" % (pp, pu, eff), ok_pairs))

    name, score = G.matches_known(g)
    cat, fam, sc = G.classify(g, m, known.get(name))
    rows.append(("collapse / improvement / discovery", "%s  (closest: %s, %d/4 slots)" % (cat, fam or "-", sc),
                 cat != "COLLAPSE"))

    passed = all(ok for _, _, ok in rows)
    return passed, rows, m
