# Author: Scott (ScottX Research)
"""The search itself. Deliberately plain.

The GA is the least interesting part of this system and that is intentional.
Sophistication in the search buys nothing here -- the space is 1.8 million
coarse genomes and the bottleneck is not finding a maximum, it is that most
maxima are noise. Everything clever lives in the gates, not here.

Population 200, tournament selection, crossover at gene boundaries, mutation
one grid step. Elitism keeps the best few. Duplicates are skipped rather than
re-evaluated, so the ledger counts distinct experiments.

WHAT THIS PRINTS AS IT RUNS
  Each generation: best and median fitness, and the share of the population
  that shares a skeleton with something we already know (genome.KNOWN). That
  share IS the collapse warning -- if it climbs to near 1.0, the search has
  folded onto a known strategy and the vocabulary is too narrow.
"""
import json
import os
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from factory import data
from factory import genome as G
from factory.config import GENERATIONS, POPULATION, TIMEFRAMES
from factory.fitness import HARD_FAIL, Ledger, fitness


def _seed_population(rng, n):
    pop = []
    guard = 0
    while len(pop) < n and guard < n * 60:
        guard += 1
        g = G.random_genome(rng)
        if G.valid(g):
            pop.append(g)
    return pop


# ---------------------------------------------------------------- parallel
# The simulator is single-threaded Python over tens of thousands of bars, so
# the population is evaluated across processes. Each worker loads the gold
# series once and keeps its own primitive cache; the series is small (H4 is
# 25k bars) so the memory cost is trivial next to the speedup.
# 4, not 6: each worker holds the gold series plus a bounded primitive
# cache, and an over-subscribed pool is what broke the first run.
# 3, not 4. Each worker holds the gold series plus a bounded primitive cache,
# and the M5 pattern arrays are ~10 MB each. Four workers broke the pool again
# on 2026-09-27 even with the cache capped, so the pool is sized for headroom
# rather than for the core count. A run that finishes slowly beats a run that
# dies at generation 0.
_WORKERS = max(1, min(3, (os.cpu_count() or 4) - 2))


def _eval_one(args):
    g, with_plateau = args
    try:
        f, m = fitness(g, with_plateau=with_plateau)
    except Exception:
        return HARD_FAIL, None
    return f, m


def _eval_population(pop, with_plateau, pool):
    if pool is None:
        out = [_eval_one((g, with_plateau)) for g in pop]
    else:
        out = list(pool.map(_eval_one, [(g, with_plateau) for g in pop], chunksize=4))
    return [o[0] for o in out], [o[1] for o in out]


def _tournament(pop, fits, rng, k=3):
    idx = rng.integers(0, len(pop), size=k)
    best = max(idx, key=lambda i: fits[i])
    return pop[int(best)]


def run(seed=0, generations=GENERATIONS, population=POPULATION, run_tag=None,
        with_plateau=True, verbose=True, workers=None):
    rng = np.random.default_rng(seed)
    run_tag = run_tag or time.strftime("run_%Y%m%dT%H%M%S")
    ledger = Ledger()
    start_ledger = len(ledger)
    nw = _WORKERS if workers is None else workers

    pop = _seed_population(rng, population)
    best_ever = (HARD_FAIL, None, None)
    t0 = time.time()

    pool = ProcessPoolExecutor(max_workers=nw) if nw > 1 else None
    if verbose:
        print("  evaluating on %d worker processes\n" % nw)
    for gen in range(generations):
        fits, mets = _eval_population(pop, with_plateau, pool)
        for g, m, f in zip(pop, mets, fits):
            ledger.record(g, m, f, run_tag)
        order = np.argsort(fits)[::-1]
        if fits[order[0]] > best_ever[0]:
            best_ever = (fits[order[0]], pop[order[0]], mets[order[0]])

        if verbose:
            known = Counter()
            for g in pop:
                name, sc = G.matches_known(g)
                known[name if sc >= 3 else "novel"] += 1
            share = 1.0 - known["novel"] / len(pop)
            fin = [f for f in fits if f > HARD_FAIL]
            print("  gen %2d | best %+7.4f | median %+7.4f | alive %3d/%d | "
                  "known-skeleton share %4.0f%% | ledger %s | %4.0fs" % (
                      gen, fits[order[0]], float(np.median(fin)) if fin else float("nan"),
                      len(fin), len(pop), 100 * share, "{:,}".format(len(ledger)),
                      time.time() - t0))

        # ---- next generation
        elite = [pop[i] for i in order[:max(2, population // 20)]]
        nxt = list(elite)
        guard = 0
        while len(nxt) < population and guard < population * 40:
            guard += 1
            a = _tournament(pop, fits, rng)
            b = _tournament(pop, fits, rng)
            child = G.crossover(a, b, rng) if rng.random() < 0.6 else json.loads(json.dumps(a))
            if rng.random() < 0.7:
                child = G.mutate(child, rng)
            if G.valid(child):
                nxt.append(child)
        pop = nxt

    if verbose:
        print("\n  %s distinct genomes added to the ledger this run (%s total)" % (
            "{:,}".format(len(ledger) - start_ledger), "{:,}".format(len(ledger))))
    # final ranking of the last population, best first, deduplicated
    fits, mets = _eval_population(pop, with_plateau, pool)
    if pool is not None:
        pool.shutdown()
    order = np.argsort(fits)[::-1]
    out, seen = [], set()
    for i in order:
        fp = G.fingerprint(pop[i])
        if fp in seen or fits[i] <= HARD_FAIL:
            continue
        seen.add(fp)
        out.append(dict(genome=pop[i], fitness=float(fits[i]), train=mets[i]))
    return out, ledger, run_tag


if __name__ == "__main__":
    import sys
    gens = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    pops = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    print("STRATEGY FACTORY — GA on TRAIN only")
    print("  population %d, %d generations, genome space %s\n" % (
        pops, gens, "{:,}".format(G.space_size())))
    top, ledger, tag = run(seed=1, generations=gens, population=pops)
    print("\n  top 10 of the final population (TRAIN numbers — not a result):")
    for r in top[:10]:
        name, sc = G.matches_known(r["genome"])
        m = r["train"]
        print("    fit %+7.4f  n=%5d mean %+7.4f t %5.2f win %4.1f%%  [%s %d/4]" % (
            r["fitness"], m["n"], m["mean"], m["t"], 100 * m["win"],
            (name or "-")[:26], sc))
        print("        %s" % G.describe(r["genome"]))
