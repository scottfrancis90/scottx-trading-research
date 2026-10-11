# Author: Scott (ScottX Research)
"""The whole pipeline: search TRAIN, gate on VALIDATE, write the report.

    python -m factory.run [generations] [population] [seed]

WHAT THIS DOES AND DOES NOT DO
  It searches TRAIN only, then puts the best distinct genomes through the
  eight gates on VALIDATE. It does NOT touch a holdout. A survivor here is a
  hypothesis with a pre-registration waiting to be written, not a result.

  Every genome evaluated -- winner or not -- goes in the ledger, because the
  ledger is the denominator that the Bonferroni gate charges against. Throwing
  away the record of a search does not undo the search.

  The report is written whether or not anything survives. A factory that only
  reports its winners is a machine for producing false positives.
"""
import sys
import time

from factory import genome as G
from factory import ga
from factory import report as R
from factory import validate as V


def main(generations=25, population=150, seed=1, top_n=12):
    t0 = time.time()
    print("STRATEGY FACTORY -- full run on %s" % ", ".join(__import__("factory.market", fromlist=["x"]).symbols()))
    print("  population %d, %d generations, seed %d" % (population, generations, seed))
    print("  genome space %s across timeframes %s" % (
        "{:,}".format(G.space_size()), ", ".join(__import__(
            "factory.config", fromlist=["x"]).TIMEFRAMES)))
    print()

    top, ledger, tag = ga.run(seed=seed, generations=generations,
                              population=population)
    print("\n  search done in %.0f min. Ledger now %s distinct genomes." % (
        (time.time() - t0) / 60.0, "{:,}".format(len(ledger))))

    print("\n  known families on VALIDATE, so IMPROVEMENT is judged against a")
    print("  real number rather than a remembered one:")
    known = V.known_on_validation()
    for name, m in known.items():
        print("    %-28s %s" % (name, "no trades" if m is None else
              "n=%d mean %+0.4f t %+0.2f" % (m["n"], m["mean"], m["t"])))

    print("\n  gating the top %d distinct genomes on VALIDATE" % top_n)
    print("  (expect zero survivors on most runs -- that is the design working)\n")
    # ---- DEDUPE BY TRADE BOOK, not by genome string.
    # Finding 82: twelve candidates differed only in their CONTEXT gene, which
    # is inert for a pattern trigger with a non-context stop and target -- six
    # different contexts produced byte-identical books. The GA burned its whole
    # population on one idea while the genome strings all looked distinct, and
    # the diversity check was fooled because it keyed on the skeleton. Two
    # genomes that place the same trades are ONE experiment, whatever they are
    # called, so gate them once.
    uniq, seen_books = [], {}
    for cand in top:
        m = cand.get("train") or {}
        key = (m.get("n"), round(float(m.get("mean", 0.0)), 9),
               round(float(m.get("total", 0.0)), 6))
        if key in seen_books:
            seen_books[key] += 1
            continue
        seen_books[key] = 1
        uniq.append(cand)
        if len(uniq) >= top_n:
            break
    dupes = sum(v - 1 for v in seen_books.values())
    if dupes:
        print("  %d candidate(s) dropped as DUPLICATE TRADE BOOKS "
              "(same trades, different gene names)" % dupes)
        print()

    gated, survivors = [], []
    for i, cand in enumerate(uniq):
        g = cand["genome"]
        passed, rows, m = V.gate(g, ledger, "validate", known)
        gated.append(dict(genome=g, passed=passed, rows=rows, valid=m,
                          train=cand["train"], fitness=cand["fitness"]))
        name, sc = G.matches_known(g)
        head = "  %2d. %s" % (i + 1, G.describe(g))
        print(head)
        print("      TRAIN fit %+0.4f  n=%d mean %+0.4f" % (
            cand["fitness"], cand["train"]["n"], cand["train"]["mean"]))
        for label, detail, ok in rows:
            print("      [%s] %-44s %s" % ("PASS" if ok else "FAIL", label, detail))
        if passed:
            survivors.append(g)
            print("      >>> SURVIVES ALL GATES")
        print()

    # ---- COLLAPSE, measured WITHIN the run.
    # The per-genome classifier only asks "does this look like a KNOWN family?".
    # It cannot see the run converging on a single NOVEL shape, which is what
    # happened on 2026-09-27: 12 of 12 candidates were the same skeleton and
    # every one was stamped DISCOVERY. A search that returns one shape twelve
    # times has explored one shape, whatever the ledger count says.
    shapes, trigs = {}, {}
    for row in gated:
        sk = G.skeleton(row["genome"])
        key = "%s|%s|%s|%s|%s" % (row["genome"]["tf"], sk["context"], sk["trigger"],
                                  sk["stop"], sk["target"])
        trig_key = row["genome"]["trigger"]["gene"]
        trigs[trig_key] = trigs.get(trig_key, 0) + 1
        shapes[key] = shapes.get(key, 0) + 1
    top_share = max(shapes.values()) / len(gated) if gated else 0.0
    print("  DIVERSITY OF THE CANDIDATES")
    print("    %d distinct skeleton(s) among the top %d" % (len(shapes), len(gated)))
    for key, cnt in sorted(shapes.items(), key=lambda x: -x[1]):
        print("      %2d x  %s" % (cnt, key))
    if top_share >= 0.7:
        print("    *** COLLAPSE: %.0f%% of the candidates are ONE shape." % (100 * top_share))
        print("        The search explored one idea, not %s." % "{:,}".format(len(ledger)))
        print("        Treat the ledger count as an upper bound on breadth, not a measure of it.")
    else:
        print("    %d distinct shapes among the candidates" % len(shapes))
    # A shape can vary while the IDEA does not. Report the trigger separately:
    # that is the thing the run actually explored.
    tshare = max(trigs.values()) / len(gated) if gated else 0.0
    print("    triggers used: %s" % ", ".join(
        "%s x%d" % (k, v) for k, v in sorted(trigs.items(), key=lambda x: -x[1])))
    if tshare >= 0.7:
        print("    *** COLLAPSE ON THE TRIGGER: %.0f%% of candidates use ONE trigger."
              % (100 * tshare))
        print("        Varying the other slots is not exploration if they change nothing.")
    print()
    path = R.write(tag, top, gated, len(ledger), known, survivors)
    print("  report written to %s" % path)
    if survivors:
        for j, g in enumerate(survivors):
            sp = R.spec(g, path.replace(".md", "_survivor%d.json" % (j + 1)))
            print("  survivor %d spec written" % (j + 1))
        print("\n  %d SURVIVOR(S). Next step is a pre-registered holdout, not an EA." % len(survivors))
    else:
        print("\n  NO SURVIVORS. Recorded as such.")
    print("  total %.0f min" % ((time.time() - t0) / 60.0))
    return survivors


if __name__ == "__main__":
    gens = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    pops = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    main(gens, pops, seed)
