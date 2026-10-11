# Author: Scott (ScottX Research)
"""The vocabulary the GA searches -- an EXAMPLE vocabulary of textbook ideas.

Replace or extend it with your own genes. Everything else in the factory
(engine, fitness, ledger, gates, holdout) works unchanged as long as this
module keeps the same functions.

A GENOME is a dict with one gene per slot plus a timeframe and a hold limit:

    {"tf": "H1", "timeout": 72, "mechanism": "breakout",
     "context": {"gene": "prior_range", "lookback": 40},
     "trigger": {"gene": "break_level", "side": "both"},
     "filter":  {"gene": "none"},
     "stop":    {"gene": "other_side"},
     "target":  {"gene": "r_multiple", "r": 2.0},
     "manage":  {"gene": "plain"}}

DESIGN AGAINST OVERFITTING
  * coarse grids only -- no `period = 37`
  * at most MAX_ACTIVE_GENES; every gene beyond the third costs fitness
  * every gene carries a mechanism tag, and a genome's mechanism is derived
    from its context and trigger. A survivor must be explainable as one of
    them or it does not go to the holdout.
  * the vocabulary is small on purpose. A bigger one finds more "winners"
    and none of them are real.

COLLAPSE / IMPROVEMENT / DISCOVERY
  A survivor is compared, by gene TYPE, with a registry of strategies you
  already know (KNOWN). Matching one is not a discovery whatever its numbers:
    COLLAPSE     same skeleton as a known family and not better than it
    IMPROVEMENT  same skeleton, clearly better on the same split
    DISCOVERY    a different skeleton that still passes every gate
"""
import json

import numpy as np

from factory import market as _MK
from factory.config import MAX_ACTIVE_GENES, TIMEFRAMES as _TF

# ---------------------------------------------------------------- vocabulary
# name -> (mechanism, {param: [coarse grid]})
CONTEXT = {   # where the two levels (rails) come from
    "prior_range": ("breakout", {"lookback": [20, 40, 100]}),        # Donchian channel
    "atr_channel": ("volatility", {"k": [1.5, 2.0, 3.0]}),            # EMA20 +/- k ATR
}
TRIGGER = {
    "break_level": ("breakout", {"side": ["both", "long", "short"]}),          # stop order at a rail
    "fade_level": ("mean_reversion", {"side": ["both", "long", "short"]}),     # limit order at a rail
    "ema_cross": ("trend", {"period": [20, 50, 100]}),                         # market order on a cross
}
FILTER = {
    "none": (None, {}),
    "trend_ema": ("trend", {"period": [100, 200]}),                   # only trade with the EMA
    "atr_band": ("volatility", {"lo": [0.5, 0.8], "hi": [1.25, 1.5, 2.0]}),   # skip dead/wild markets
}
STOP = {
    "other_side": (None, {}),                                         # the opposite rail
    "atr_mult": (None, {"k": [1.0, 1.5, 2.0, 3.0]}),
}
TARGET = {
    "r_multiple": (None, {"r": [1.0, 1.5, 2.0, 3.0]}),
    "opposite_level": (None, {}),                                     # the other rail
}
MANAGE = {
    "plain": (None, {}),
    "trail": (None, {"k": [1.0, 2.0, 3.0]}),                          # trail k ATR behind the best price
}

TIMEFRAMES = _MK.timeframes(_TF)
TIMEOUT_GRID = [24, 72, 200]          # HOURS, so the hold means the same thing on every timeframe

SLOTS = (("context", CONTEXT), ("trigger", TRIGGER), ("filter", FILTER),
         ("stop", STOP), ("target", TARGET), ("manage", MANAGE))

# ---------------------------------------------------------------- known families
# What you already know. A survivor matching one of these on gene TYPE (3 of 4
# slots) is not a discovery.
KNOWN = {
    "Donchian breakout (textbook)": dict(context="prior_range", trigger="break_level",
                                         stop="other_side", target="r_multiple"),
}
# The same families as runnable genomes, measured on the validation split so
# IMPROVEMENT is judged against a real number, not a remembered one.
KNOWN_PROBES = {
    "Donchian breakout (textbook)": dict(
        tf=TIMEFRAMES[0], timeout=72, mechanism="breakout",
        context=dict(gene="prior_range", lookback=40), trigger=dict(gene="break_level", side="both"),
        filter=dict(gene="none"), stop=dict(gene="other_side"),
        target=dict(gene="r_multiple", r=2.0), manage=dict(gene="plain")),
}


def skeleton(g):
    return dict(context=g["context"]["gene"], trigger=g["trigger"]["gene"],
                stop=g["stop"]["gene"], target=g["target"]["gene"])


def matches_known(g):
    """(family name, slots matched) for the closest known family, or (None, 0)."""
    sk = skeleton(g)
    best, score = None, 0
    for name, k in KNOWN.items():
        s = sum(1 for slot, gene in k.items() if sk.get(slot) == gene)
        if s > score:
            best, score = name, s
    return best, score


def classify(g, cand_metrics, known_metrics):
    """COLLAPSE / IMPROVEMENT / DISCOVERY, decided on gene types and numbers."""
    name, score = matches_known(g)
    if score < 3:
        return "DISCOVERY", name, score
    if known_metrics is None:
        return "IMPROVEMENT?", name, score
    better = (cand_metrics["mean"] > known_metrics["mean"] * 1.20
              or (np.isfinite(cand_metrics.get("rdd", np.nan))
                  and np.isfinite(known_metrics.get("rdd", np.nan))
                  and cand_metrics["rdd"] > known_metrics["rdd"] * 1.20))
    return ("IMPROVEMENT" if better else "COLLAPSE"), name, score


# ---------------------------------------------------------------- genome ops
def _pick(rng, table):
    gene = rng.choice(sorted(table.keys()))
    mech, grids = table[gene]
    d = {"gene": str(gene)}
    for p, grid in grids.items():
        v = grid[int(rng.integers(len(grid)))]
        d[p] = v.item() if hasattr(v, "item") else v
    return d, mech


def _mechanism(g):
    mechs = [m for slot, table in SLOTS if slot in ("context", "trigger")
             for m in [table[g[slot]["gene"]][0]] if m]
    return "+".join(sorted(set(mechs))) or "unclassified"


def random_genome(rng):
    g = {}
    for slot, table in SLOTS:
        g[slot], _ = _pick(rng, table)
    g["tf"] = TIMEFRAMES[int(rng.integers(len(TIMEFRAMES)))]
    g["timeout"] = TIMEOUT_GRID[int(rng.integers(len(TIMEOUT_GRID)))]
    g["mechanism"] = _mechanism(g)
    return g


def n_active(g):
    n = 2                                        # context and trigger always count
    n += g["filter"]["gene"] != "none"
    n += g["stop"]["gene"] != "other_side"
    n += g["target"]["gene"] != "r_multiple"
    n += g["manage"]["gene"] != "plain"
    return int(n)


def valid(g):
    """reject nonsense at generation time rather than wasting a simulation"""
    tr, st, tg = g["trigger"]["gene"], g["stop"]["gene"], g["target"]["gene"]
    # the opposite rail is a stop only for a breakout, and a target only for a fade
    if st == "other_side" and tr != "break_level":
        return False
    if tg == "opposite_level" and tr != "fade_level":
        return False
    if g["filter"]["gene"] == "atr_band" and g["filter"]["lo"] >= g["filter"]["hi"]:
        return False
    if n_active(g) > MAX_ACTIVE_GENES:
        return False
    return True


def mutate(g, rng):
    """one grid step on one gene, or (30%) a new gene in that slot"""
    h = json.loads(json.dumps(g))
    slot, table = SLOTS[int(rng.integers(len(SLOTS)))]
    if rng.random() < 0.3:
        h[slot], _ = _pick(rng, table)
    else:
        grids = table[h[slot]["gene"]][1]
        if grids:
            p = sorted(grids.keys())[int(rng.integers(len(grids)))]
            grid = grids[p]
            i = grid.index(h[slot][p]) if h[slot][p] in grid else 0
            h[slot][p] = grid[int(np.clip(i + (1 if rng.random() < 0.5 else -1), 0, len(grid) - 1))]
    if rng.random() < 0.15:
        h["tf"] = TIMEFRAMES[int(rng.integers(len(TIMEFRAMES)))]
    if rng.random() < 0.15:
        h["timeout"] = TIMEOUT_GRID[int(rng.integers(len(TIMEOUT_GRID)))]
    h["mechanism"] = _mechanism(h)
    return h


def crossover(a, b, rng):
    """swap whole genes at slot boundaries -- never half a gene"""
    h = json.loads(json.dumps(a))
    for slot, _ in SLOTS:
        if rng.random() < 0.5:
            h[slot] = json.loads(json.dumps(b[slot]))
    if rng.random() < 0.5:
        h["tf"] = b["tf"]
    if rng.random() < 0.5:
        h["timeout"] = b["timeout"]
    h["mechanism"] = _mechanism(h)
    return h


def neighbours(g):
    """every one-grid-step neighbour, for the plateau test"""
    out = []
    for slot, table in SLOTS:
        for p, grid in table[g[slot]["gene"]][1].items():
            cur = g[slot].get(p)
            if cur not in grid:
                continue
            i = grid.index(cur)
            for j in (i - 1, i + 1):
                if 0 <= j < len(grid):
                    h = json.loads(json.dumps(g))
                    h[slot][p] = grid[j]
                    if valid(h):
                        out.append(h)
    return out


def fingerprint(g):
    """the identity used by the ledger: two genomes with the same fingerprint
    are the same experiment and must not be counted twice."""
    return json.dumps({k: g[k] for k in ("tf", "timeout", "context", "trigger",
                                         "filter", "stop", "target", "manage")}, sort_keys=True)


def describe(g):
    def part(slot):
        d = g[slot]
        extra = ", ".join("%s=%s" % (k, v) for k, v in sorted(d.items()) if k != "gene")
        return d["gene"] + ("(" + extra + ")" if extra else "")
    return "%s %s | ctx %s | trig %s | filt %s | stop %s | tgt %s | manage %s | hold %dh" % (
        g["tf"], g["mechanism"], part("context"), part("trigger"), part("filter"),
        part("stop"), part("target"), part("manage"), g["timeout"])


def rules_in_words(g):
    """the genome as plain English, so a person can say whether it makes sense"""
    c, tr, f, st, tg, mg = (g[k] for k in ("context", "trigger", "filter", "stop", "target", "manage"))
    out = []
    if c["gene"] == "prior_range":
        out.append("Rails: the highest high and lowest low of the previous %d bars." % c["lookback"])
    else:
        out.append("Rails: the 20-bar EMA plus and minus %.1f ATR." % c["k"])
    side = {"both": "both rails", "long": "the long side only", "short": "the short side only"}
    if tr["gene"] == "break_level":
        out.append("Enter with a STOP order beyond a rail (%s): follow the breakout." % side[tr["side"]])
    elif tr["gene"] == "fade_level":
        out.append("Enter with a LIMIT order at a rail (%s): fade the move." % side[tr["side"]])
    else:
        out.append("Enter at market on the next bar after the close crosses the %d EMA." % tr["period"])
    if f["gene"] == "trend_ema":
        out.append("Only trade in the direction of the %d EMA." % f["period"])
    elif f["gene"] == "atr_band":
        out.append("Only when ATR is %.2f-%.2f x its recent median." % (f["lo"], f["hi"]))
    out.append("Stop at the opposite rail." if st["gene"] == "other_side" else "Stop %.1f ATR from entry." % st["k"])
    out.append("Target %.1f R." % tg["r"] if tg["gene"] == "r_multiple" else "Target the opposite rail.")
    if mg["gene"] == "trail":
        out.append("Trail the stop %.0f ATR behind the best price." % mg["k"])
    out.append("Close after %d hours if neither is hit. Timeframe %s." % (g["timeout"], g["tf"]))
    return out


def space_size():
    """how many distinct genomes exist -- the denominator before a single one is run"""
    total = 1
    for _, table in SLOTS:
        s = 0
        for _, (_, grids) in table.items():
            k = 1
            for grid in grids.values():
                k *= len(grid)
            s += k
        total *= s
    return total * len(TIMEFRAMES) * len(TIMEOUT_GRID)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    print("genome space: %s distinct genomes" % "{:,}".format(space_size()))
    shown = 0
    while shown < 5:
        g = random_genome(rng)
        if valid(g):
            shown += 1
            print("\n  " + describe(g))
            for line in rules_in_words(g):
                print("     - " + line)
