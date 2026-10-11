# Finding 136 - GA restored with SMC genes; first run: COLLAPSE, no survivors; factory defects 15-16 (2026-10-08)

factory/ restored from _archive_ga (copies). New genes (factory/patterns_smc.py):
ob_retest (kind bos/displacement/fvg, nth, need_liq, formed any/London/Asia),
liq_grab (LiquidityX), session_sweep (PDH/PDL/Asia in London/NY), filters
bos_bias (TF/H4/D1) and pd_zone, target opposite_ob (any/Asia). All truncation-
tested causal on M30/H1/H4/D1. The factory's gold data is UTC (weekly open
22/23h) -- the first draft assumed NY+7 and would have shifted sessions 7 hours.
Run gold_20261008T123642 (seed 11, 25 gen x 150, M30/H1/H4/D1, SMC triggers
only): 1,460 new genomes (ledger 10,255). COLLAPSE on the trigger: all 12
candidates ob_retest(kind=bos, nth=0), M30, swing stop, 1.5R. TRAIN +0.02 R ->
VALIDATE -0.13 R (halves -0.05/-0.21). No survivors.
DEFECT 15: genome.fingerprint/describe omitted `manage` -> genomes differing
only in partial/trail counted as one experiment; report hid the gene. Fixed
(plain still omitted, so old ledger lines keep identity).
DEFECT 16: the inverted/shuffled controls rebuilt R from the trade's FINAL stop
(moved by partial/trail) and walked the mirror unmanaged -> mirror +0.5004 on a
rule whose true mirror is +0.019. simulate now records stop0; the mirror uses it
and the rule's own management. Neither defect changed this run's verdict (all
died at "both halves positive"), but both would corrupt later gates.

---
[All findings](../README.md)
