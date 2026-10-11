# Finding 137 - GA rerun (seed 12) with defects 15-16 fixed and Asia/opposite-OB genes: no survivors (2026-10-08)

Run gold_20261008T132344, 25 x 150, M30/H1/H4/D1, SMC triggers only. 1,639 new
genomes (ledger 11,894; Bonferroni bar |t| >= 5.08). Top 12: ob_retest x10,
liq_grab, session_sweep -> COLLAPSE on the trigger (83%). Best candidate H1
ob_retest(bos, every return) + 3 ATR stop, 3R, trail 1.5: TRAIN -0.035,
VALIDATE halves -0.001 / -0.043. Mirror control now sane (-0.055). Explored:
OB formed in London 32 genomes (best TRAIN +0.035), Asia 11 (best -0.036);
Asia OB + opposite-OB target 6 genomes, best TRAIN -0.044. bos_bias 15 genomes,
pd_zone 52. Nothing beats random on VALIDATE.

---
[All findings](../README.md)
