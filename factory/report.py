# Author: Scott (ScottX Research)
"""What a run produced, written down so it can be argued with.

Two outputs:
  * a human page -- the rules in words, the numbers, and which gate killed
    what. Including the failures, because a factory that only reports its
    winners is a machine for producing false positives.
  * spec.json -- a survivor's rules in a form an EA template can read.

The report always states the DENOMINATOR (how many genomes were tried) next
to any result, because a number without its denominator is not a result.
"""
import json
import os
import time

from factory import genome as G
from factory import market as MK
from factory.config import OUT


def write(run_tag, top, gated, ledger_size, known, survivors):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "%s.md" % run_tag)
    L = ["# Factory run `%s`" % run_tag, "", "_%s_ -- symbols: %s" % (time.strftime("%Y-%m-%d %H:%M"), ", ".join(MK.symbols())), "",
         "**Denominator: %s distinct genomes have now been evaluated** across all runs. "
         "Every number below is charged against that." % "{:,}".format(ledger_size), ""]
    for name, k in known.items():
        if k:
            L += ["Reference -- %s on the validation split: n=%d, mean %+0.4f R, t %+0.2f." % (name, k["n"], k["mean"], k["t"]), ""]
    L += ["## Survivors", ""]
    if not survivors:
        L.append("**None.** Expect this most runs; it is the design working, not failing. "
                 "The gates below name what killed each candidate.")
    for g in survivors:
        L += ["### %s" % G.describe(g), ""] + ["* %s" % s for s in G.rules_in_words(g)] + [""]
    L += ["", "## Every candidate and the gate that killed it", "",
          "| genome | train mean | validate mean | died at |", "|---|---|---|---|"]
    for row in gated:
        died = next((n for n, _, ok in row["rows"] if not ok), "survived")
        vm = row["valid"]
        L.append("| `%s` | %+0.4f | %s | %s |" % (G.describe(row["genome"])[:80], row["train"]["mean"],
                                               ("%+0.4f" % vm["mean"]) if vm else "no trades", died))
    L += ["", "## Gate detail", ""]
    for row in gated:
        L += ["**`%s`**" % G.describe(row["genome"]), ""]
        L += ["* %s -- %s -- **%s**" % (n, d, "ok" if ok else "FAIL") for n, d, ok in row["rows"]] + [""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return path


def spec(g, path=None):
    """a survivor in a form an EA template can read"""
    s = dict(symbols=list(MK.symbols()), timeframe=g["tf"], hold_hours=g["timeout"],
             context=g["context"], trigger=g["trigger"], filter=g["filter"], stop=g["stop"],
             target=g["target"], manage=g["manage"], mechanism=g["mechanism"],
             rules_in_words=G.rules_in_words(g))
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=1)
    return s
