# Finding 81 - the molecules run: no survivors, and a total collapse the detector did not catch.

*2026-09-27. Gold, all five timeframes, population 150, 25 generations, seed 1.
TRAIN search, VALIDATE gating. No holdout touched.*

First run with the nine named molecules in the vocabulary (Finding 80).
Genome space 26,907,098,400. Ledger 1,983 -> **3,206**. Runtime 82 minutes.

### Result: no survivors

All twelve gated candidates failed the SAME gate -- Bonferroni over 28,854
(3,206 genomes x 9 resets), needing |t| >= 4.78. Best was t +3.42.

| # | TRAIN mean | VALIDATE mean | t | died at |
|---|---|---|---|---|
| 1 | +0.3225 (n=1870) | +0.1368/+0.1885 halves | +3.32 | Bonferroni |
| 3 | +0.3001 (n=1978) | +0.1334/+0.1850 | +3.42 | Bonferroni |
| 5 | +0.2650 (n=2211) | +0.1229/+0.1923 | +3.42 | Bonferroni |
| 10 | +0.2520 (n=1424) | -0.0470/+0.1418 | +0.85 | halves, Bonferroni, inverted |

Eleven of twelve passed the inverted control (edges +0.31 to +0.74), the
shuffled control, both-halves, and plateau. They died on multiple testing
alone, which is the correct outcome for a t of 3 against a denominator of
28,854.

### The real result: a COLLAPSE, and the detector said DISCOVERY

**Twelve of twelve candidates are the identical skeleton:**

```
H1 | ctx vol_expansion | trig fade_level(side=down) | stop atr_mult | tgt r_multiple
```

Only the filter, the timeout, `rel` and `r` differ. The run converged by
generation 8 (best fitness pinned at +0.2047 from gen 8 to gen 24) and spent
sixteen generations producing variations of one idea.

Meanwhile the per-genome classifier reported **"known-skeleton share 0%"** and
stamped every single candidate **DISCOVERY**. It was not lying: it asks only
"does this resemble StraddleX / AsianRangeX / Frequency?", and this shape
resembles none of them. **It cannot see a run collapsing onto a single NOVEL
shape.** That is precisely the failure the user warned against on 2026-09-26:
*"Don't hide a collapse and call it discovery."*

**Fixed.** `factory/run.py` now measures diversity WITHIN the run -- distinct
skeletons among the gated candidates -- and prints `*** COLLAPSE` when one
shape holds 70% or more. A ledger count of 3,206 is an upper bound on breadth,
not a measure of it.

### The molecules were not used. At all.

**Zero of the nine named patterns appear in the top twelve.** Given sand and
bricks, the GA went back to sand: `fade_level` is an atom, and it beat every
molecule on TRAIN fitness. The bricks cost 9 gene options and 23 billion genome
combinations and bought nothing on this run.

Two readings, and the honest answer is that this run cannot separate them:
  1. Order carries no information -- sequencing weak components makes a more
     complicated coin flip, exactly as was predicted before the run.
  2. The GA never explored them. It found `fade_level` early, fitness plateaued
     at generation 8, and selection pressure removed the alternatives before
     the molecule branch of the space was searched at all.

The collapse makes (2) the more likely explanation and means (1) is NOT
established. A search that converges by generation 8 has not tested 26.9
billion genomes; it has tested one neighbourhood.

### Note for whoever runs this shape again

`fade_level` is the LIMIT-order gene, and it is the same family that produced
the Finding 77 artifact. The pruning defect is fixed and these numbers are
post-fix. But before this shape is ever pre-registered, it must first be
re-measured against an implementable order model the way Finding 77 was --
matching trade counts prove nothing; check the overlap of the actual trades.

### Also fixed

`report.py` expects dicts; `run.py` was passing tuples, so the report write
crashed AFTER an 82-minute search had completed and been gated. The results
survived only because they were in the log. Fixed, plus workers reduced 4 -> 3
and the primitive cache 400 MB -> 220 MB after a `BrokenProcessPool` on retest.

**Status: no tradable rule. The molecules are untested, not disproved.**

---

---
[All findings](../README.md)
