# Finding 82 - the molecules-only run: no survivors, and the context gene was doing nothing at all.

*2026-09-27. Pre-registered in `factory/runs/PREREG_molecules.md` BEFORE the run.
Trigger slot restricted to the nine molecules, space 22,353,589,440.
Population 150, 25 generations, seed 2. Ledger 3,206 -> 5,205. Runtime 18 min.*

Finding 81 left one question: were the molecules useless, or merely never
searched? This removed the atoms from the trigger slot so they could not be
smothered.

### Every prediction held

| predicted | happened |
|---|---|
| no survivors | **none** |
| best TRAIN fitness below +0.2047 | **-0.0235**, never positive in 25 generations |
| another collapse | **12 of 12 used one molecule**, `range_expand_fade` |
| sequencing may add nothing | supported, see below |

### Why it failed: three gates at once, and a sign flip

All twelve candidates were identical books: n=876, TRAIN mean **+0.0594**;
VALIDATE halves **-0.0168 / -0.0483**, t **-0.58** against a required 4.88.

It did not merely fail significance -- **it changed sign out of sample.**
Plateau was 0% of neighbours positive, so it was a spike, not a region. A rule
that is positive on TRAIN, negative on VALIDATE, and surrounded by losing
neighbours is overfitting, and all three gates said so independently.

The inverted control gave edge +0.0980, but with the rule itself at -0.033 on
validation **both directions lose.** That is the cost signature this project
has now seen in every family it has tested.

### The real finding: an inert gene, and a diversity metric fooled by it

Six different context genes, same trigger/stop/target:

```
  ctx vwap_band       n=876 mean +0.059426 total +52.0567
  ctx volume_value    n=876 mean +0.059426 total +52.0567
  ctx vol_expansion   n=876 mean +0.059426 total +52.0567
  ctx swing_levels    n=876 mean +0.059426 total +52.0567
  ctx vol_contraction n=876 mean +0.059426 total +52.0567
  distinct trade books produced by six different contexts: 1
```

**Byte-identical.** A pattern trigger resolves its own direction and entry, so
with a `swing` stop and an `r_multiple` target the context gene is never read.
The GA spent its entire population on ONE trade book wearing twelve names.

This also fooled the collapse detector added only hours earlier in Finding 81.
It keyed on the SKELETON, counted five distinct context genes, and reported
*"no collapse: the top candidates span 5 shapes"* -- while the trigger was
identical in all twelve. Second blind spot in the same guard.

**Both fixed.** `factory/run.py` now (a) dedupes candidates by TRADE BOOK
before gating, because two genomes that place the same trades are one
experiment whatever they are called, and (b) reports trigger-level collapse
separately, because varying slots that change nothing is not exploration.

The ledger counted those twelve as twelve distinct genomes. That inflates the
Bonferroni denominator, which is conservative rather than dangerous, but it
means **the ledger overstates how much of the space has really been searched.**

### So: does sequencing carry information?

Best evidence to date says no, but it is not proven. Eight of the nine
molecules never reached the top twelve in either run. The one that did
(`range_expand_fade`) is the least sequence-like of them -- an expansion bar
followed by a bar closing the other way, which is nearly a single-bar pattern.
The genuinely sequential ones (sweep-then-reclaim, break-then-retest,
cross-then-confirm) were bred out early in both runs.

**Status: no tradable rule. 5,205 genomes in the ledger; Bonferroni bar now
|t| >= 4.88 and rising.**

---

---
[All findings](../README.md)
