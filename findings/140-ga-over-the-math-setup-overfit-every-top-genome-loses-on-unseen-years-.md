# Finding 140 - GA over the "Math" setup: overfit, every top genome loses on unseen years (2026-10-09)

ml/math_ga.py (out ml/math_ga_out.txt). 599 genomes (pair, TF, k, winner tp/sl, cap,
EURCHF filter), TRAIN 2017-2021, VALIDATE 2022-2026 once. Top 10 all EURNZD/NZDCHF D1
k=0.5 tp=2: TRAIN +0.57..+0.62 R per setup -> VALIDATE -0.25..-0.52 R (win 27-35%).
The EURCHF filters it picked (quiet<0.3 and moving>0.5 both appear) contradict each
other -- a sign of fitting noise. The only setting positive in both halves remains the
plain pre-registered EURUSD/USDCHF D1 k=1 (+0.16 / +0.27 R), not confirmed by the
cross-check pairs.

---
[All findings](../README.md)
