# Results: R01-R11

**Author: Scott (ScottX Research)**

The experiment ledger for the core ML study, newest first: R11 (the single final test) at the top, R01 (the data audit) at the bottom. Every experiment is recorded with its hypothesis and outcome, including the failures, so any positive result can be discounted honestly for the number of tests behind it.

---

## R11 - Final test evaluation (run once)

**Date** 2026-08-28
**Hypothesis** Pre-registered confirmatory run. Nothing was promoted to this
stage; the run exists because a negative confirmed on untouched data is a
stronger claim than one confirmed on data already examined.
**Data** Test split, **2023-03-01 to 2024-07-19, 8,214 bars, first and only
read.** Buy-and-hold +$572.9/oz over the period.
**Model** `logit_l2_C0.1`, H1 k=8, overlapping book, expanding walk-forward.
All parameters fixed in R02/R05/R06 before this file was written.

### Result

| strategy | acc | drift | **net** | t(ind) | turnover | maxDD |
|---|---:|---:|---:|---:|---:|---:|
| **logit_l2_C0.1** | 0.5116 | 0.5212 | **−441.1** | +0.77 | 0.088 | 469.9 |
| always_long | 0.5212 | 0.5212 | +580.2 | +2.82 | 0.000 | 241.1 |
| always_short | 0.4780 | 0.5212 | −580.2 | −2.82 | 0.000 | 673.5 |
| coin_flip | 0.4859 | 0.5212 | −1,668.5 | −2.22 | 0.991 | 1,683.1 |

The model's accuracy (0.5116) is **below** the drift base rate (0.5212). At
zero cost it still loses **−$355.6**. Negative in both test years.

### The one significant number in the study, and why it is not a strategy

`always_long` on the test split has **t = +2.82** - the only conventionally
significant result anywhere in this project. It is drift, not skill: gold rose
$573/oz between 2023-03 and 2024-07. R03 already established that the drift is
**not stable** (train P(up) 0.5151, validation 0.4972, test 0.5263), and R06's
fold-level t for `always_long` was only +1.55. Buying gold worked in 2023-24
because gold went up. That is a directional view on gold, not a finding of
this research, and not something ML contributed to.

**Status: complete. The test split is spent.**

---

## R10 - Cost sensitivity, calibration, regimes

**Date** 2026-08-28
**Hypothesis** That the loss is a cost problem, or is confined to particular
years, sessions or volatility regimes.
**Data** 24,000 walk-forward out-of-sample bars, train + validation. Test not
read.
**Model** `logit_l2_C0.1`, fixed in R06 before these breakdowns existed.

### Finding 1 - the loss survives zero cost, which settles the question

| cost | model net | always_long | model gross |
|---|---:|---:|---:|
| **0.0× spread** | **−305.5** | +644.9 | −305.5 |
| 1.0× spread | −684.1 | +644.7 | −305.5 |
| 3.0× spread | −1,441.2 | +644.4 | −305.5 |

**At zero transaction cost the model still loses $305.5.** No spread
improvement, execution upgrade, broker change or rebate can rescue a negative
gross signal. This retires the "costs are killing an edge" hypothesis
permanently - the same hypothesis that consumed much of the retired project.

### Finding 2 - probabilities are not informative

| decile | mean P(up) | actual P(up) |
|---|---:|---:|
| 1 | 0.4155 | 0.4900 |
| 5 | 0.4960 | 0.5133 |
| 9 | 0.5492 | 0.5900 |
| 10 | 0.5921 | 0.5333 |

Decile correlation +0.445, but the top-minus-bottom actual spread is only
**+0.0433**, and the top decile is *lower* than the ninth. The model is
overconfident at both extremes (predicting 0.4155 where reality is 0.4900,
0.5921 where reality is 0.5333). Monotone-but-flat and non-monotone at the
tail: useless for position sizing.

### Finding 3 - the failure is universal, not regime-specific

| breakdown | profitable |
|---|---|
| years | **1 of 6** (2018, on 259 bars) |
| sessions | **1 of 4** (Asian, +$10.8) |
| volatility regimes | **0 of 3** |

There is no year, session or regime where this works. A model that failed
only in, say, high volatility would suggest a filter; failing everywhere
suggests there is nothing there.

**Status: complete.**

---

## R09 - Re-test of the R08 survivors

**Date** 2026-08-28
**Hypothesis** That the 3 cells with positive validation net in R08 represent
real structure rather than selection across 32 cells.
**Data** As each cell. Train → validation. Test not read.
**Model** Inherited from R08 unchanged. Nothing tuned.
**Test** R08's own pre-registered rule: survivors must pass the rotation null
and walk-forward.

### Result - all three fail

| cell | valid net | null max | walk-fwd net | always_long | verdict |
|---|---:|---:|---:|---:|---|
| H4 k=1 hgb | +284.8 | +110.7 | **−467.1** | +485.5 | fails |
| H4 k=8 hgb | +97.1 | +289.3 | −5.4 | +506.6 | fails |
| M30 k=16 logit | +55.3 | +303.3 | +53.2 | +515.5 | fails |

### Finding - the one cell that passed a null still died out of sample

**H4 k=1 passed the rotation null**: 0 of 12 rotated-label refits matched it
(empirical p ≤ 0.077). It is the only cell in the entire project to clear
that bar. Under walk-forward it then lost **−$467.1**, profitable in 5 of 12
folds, fold-level t = −1.59.

This is the clearest available demonstration of why one holdout split is not
enough. A cell can look real against a permutation null and still be an
artifact of *where the split happened to fall*. Two independent tests were
needed, and they disagreed.

The other two cells were reproduced by rotated labels roughly half the time
(p ≤ 0.538 and p ≤ 0.462) - noise on the first test, before walk-forward was
even needed.

**Status: complete. No candidate survives. Nothing earned a test evaluation
on merit.**

---

## R08 - Timeframe × horizon sweep

**Date** 2026-08-28
**Hypothesis** That the H1 / 8-hour null is specific to that cell, and some
other timeframe or horizon carries a learnable edge.
**Data** M15, M30, H1, H4 × horizons 1, 4, 8, 16. Train → validation. Test not
read.
**Model** Two fixed models per cell (`logit_l2_C0.1`, `hgb_d2_lr0.03`), one
fixed position rule. Nothing tuned per cell. **32 cells, all reported.**

### Result

**3 of 32 cells had positive validation net.** Best +284.8, worst −2,718.6,
median −250.9. All three were sent to R09 and all three failed.

### Finding - M15 shows exactly the microstructure R02 predicted

| cell | val gross | val cost | val net |
|---|---:|---:|---:|
| M15 k=1 logit | **+570.7** | −3,158.5 | −2,587.9 |
| M15 k=4 logit | **+361.5** | −1,033.3 | −671.8 |
| M30 k=1 logit | **+792.2** | −2,033.5 | −1,241.4 |
| M30 k=1 hgb | **+673.3** | −2,068.9 | −1,395.6 |

Short horizons on fast timeframes are **consistently positive gross and
catastrophically negative net** - costs 3-6× the gross. This is the bid-ask
bounce R02 identified through the Lo-MacKinlay variance ratio, showing up
again through a completely different route. The models are successfully
detecting it. It is unharvestable by construction: capturing the oscillation
means paying the spread that creates it.

**Recorded as a confirmed, correctly-predicted, permanently untradable
effect.**

### Note on the sweep's own arithmetic

The script prints "roughly 16 of 32 would clear zero by chance". That is only
right for a zero-centred distribution. Costs shift the whole net distribution
negative, so 3 of 32 is consistent with a **zero gross edge minus costs**, not
with 32 coin flips. Correcting my own line rather than leaving it to be
misread.

**Status: complete. The null is not specific to H1 / 8 hours.**

---

## R07 - Model-free feature information, and the ceiling

**Date** 2026-08-28
**Hypothesis** Two objections to the R05/R06 null: "your models are bad" and
"the opportunity is too small anyway". Both are answered here **without
fitting a model**, so neither can be blamed on one.
**Data** H1, k=8, train split only, 3,431 non-overlapping rows.
**Model** None.

### Finding 1 - the ceiling is enormous, so failure is failure to predict

A perfect forecast, traded through the identical cost model:

| | perfect next-bar sign | perfect 8-hour sign |
|---|---:|---:|
| train | **+$40,663** | **+$17,482** |
| validation | **+$19,597** | **+$7,811** |

The opportunity is not the constraint. A perfect 8-hour directional call
earns **$7,811/oz net on the validation bars alone**, against which the best
model in R05 earned **+$55 gross**. That is **0.7% of the available
opportunity** - not a near miss, and not a costs problem.

### Finding 2 - no feature carries information, model-free

Each feature was cut into equal-count bins and the top-minus-bottom
difference in forward return t-tested on non-overlapping rows only.

| feature | Spearman | t(top−bot) | monotonicity |
|---|---:|---:|---:|
| tod_sin | −0.0263 | −2.22 | −0.52 |
| kurt_72 | +0.0452 | +2.22 | +0.78 |
| loc_24 | −0.0045 | +1.64 | +0.62 |
| loc_72 | +0.0116 | +1.55 | +0.44 |
| tickvol_over_med72 | +0.0381 | +1.34 | +0.65 |
| … 28 more, all \|t\| < 1.2 | | | |

- **33 features tested. Bonferroni 5% threshold |t| > 3.17 → 0 pass.**
- Nominal 5% threshold |t| > 1.96 → **2 pass, against 1.7 expected by chance.**

Two nominal hits out of 33 is exactly what pure noise produces. No Spearman
correlation exceeds |0.046|.

### Finding 3 - the strongest feature, traded directly, still loses

`tod_sin` (the top feature by |t|, train-selected) traded on its sign alone:
validation net **−$284.7**, gross **−$44.6**, accuracy 0.5041. Its apparent
train-side gross of +$160.5 does not survive to validation, and never covered
its own turnover even in training.

**Conclusion: the features do not carry exploitable directional information
about the next 8 hours of gold. This is measured, not inferred from a model's
failure.**

**Status: complete. NEGATIVE RESULT, model-free.**

---

## R06 - Walk-forward

**Date** 2026-08-28
**Hypothesis** That R05's failure is an artifact of one unlucky
train/validation boundary, and repeated refitting on rolling windows would
show the models working in other regimes.
**Data** H1, k=8, expanding window over train + validation. 16 folds, minimum
12,000 training bars, 1,500 bars traded per fold, 24,000 out-of-sample bars,
2018-12 to 2023-01. Labels purged at every window edge. **Test excluded.**
**Model** Three pre-registered fixed models, plus an ADAPTIVE arm that
re-selects the best of all 54 configurations at every fold using an inner
validation window carved from the end of the training data.

### Result - the hypothesis is rejected, and the adaptive arm is worst

| strategy | gross | cost | **net** | acc | folds + | fold t |
|---|---:|---:|---:|---:|---:|---:|
| logit_l2_C0.1 | −305.5 | −378.6 | **−684.1** | 0.5001 | 4/16 | −2.51 |
| logit_l1_C0.01 | −408.2 | −345.0 | **−753.2** | 0.4965 | 4/16 | −1.95 |
| hgb_d2_lr0.03 | −839.3 | −336.4 | **−1,175.7** | 0.5002 | 4/16 | −4.00 |
| **adaptive** | −824.3 | −523.5 | **−1,347.8** | 0.4881 | **1/16** | **−4.71** |
| always_long | +644.9 | −0.2 | +644.7 | 0.5170 | 11/16 | +1.55 |

### Finding 1 - the selection procedure actively destroys value

The adaptive arm **is the research pipeline itself**: score every candidate on
held-out recent data, take the winner, deploy it. Run honestly, that
procedure produced the **worst** result in the study - profitable in **1 fold
of 16**, t = −4.71, and it paid 50% more in costs than the fixed models
because it kept switching to higher-turnover configurations.

It chose a different configuration in **14 of 16 folds**. There is no stable
"best model" to find; the inner-window winner is noise, and following it is
worse than picking one model and leaving it alone.

**This is the single most important result in the project.** It is not that a
particular model failed. It is that the standard method for finding a model
has negative expected value on this data.

### Finding 2 - consistency, not variance, is what kills it

The failure is not one catastrophic fold. All three fixed models are negative
in 12 of 16 folds, with fold-level t between −1.95 and −4.00. A model that is
merely unlucky produces a wide spread around zero; these produce a narrow
spread around a negative mean, which is what paying costs for a zero signal
looks like.

### Honest note on always_long

`always_long` nets +$644.7 over these bars, but its fold-level t is **+1.55 -
not significant**, and 2019-2020 (the gold rally) is inside this window. It is
the comparator, not a recommendation. R03 already showed the drift is not
stable across splits.

**Status: complete. NEGATIVE RESULT, confirmed out of sample across 16 folds.**

---

## R05 - First model fits

**Date** 2026-08-28
**Hypothesis** That a regularised linear or gradient-boosted model, given 33
scale-free features, can predict the sign of the 8-hour forward return well
enough to beat `always_long` after costs on validation.
**Data** H1, k=8. Fitted on **train only** (27,448 rows); scored on
validation (9,338 rows). Test not read.
**Model** 9 pre-registered models × 6 pre-registered position rules = **54
configurations, every one reported.**

### Result - the hypothesis is rejected

**0 of 54 configurations made money on validation.** Range −$39.6 to −$841.6,
median −$403.6.

| model / rule | train net | val gross | val cost | val net | acc | turn |
|---|---:|---:|---:|---:|---:|---:|
| logit_l1_C0.01 / hold, d0.00 | +397 | **+55.6** | −95.2 | **−39.6** | 0.5136 | 0.075 |
| logit_l1_C0.01 / hold, d0.02 | +365 | −10.6 | −61.6 | −72.2 | 0.5121 | 0.047 |
| hgb_d3_lr0.1 / hold, d0.00 | **+7,797** | −271.1 | −113.7 | −384.7 | 0.5048 | 0.089 |
| logit_l2_C0.1 / inst, d0.00 | −410 | −343.2 | −498.4 | −841.6 | 0.5042 | 0.393 |

### Finding 1 - the gross edge is approximately zero, not "eaten by costs"

The best cell earns **+$55.6 gross** across 9,338 hours on an instrument
trading near $1,800. That is not an edge that costs destroyed; it is a zero.
Only 3 of 54 cells have positive gross at all, and the largest is +$188 with
a −$421 cost attached. This distinction was worth making explicitly: the
retired project spent months on configurations where cost hid a zero.

### Finding 2 - train fit is uncorrelated with validation result

`corr(train net, valid net) = +0.088` across the 54 cells. HGB at depth 3
earns **+$7,797** in training and **−$385** in validation - a 20× in-sample
result that inverts out of sample. 39 of 54 cells are profitable in training;
0 of 54 in validation. This is a textbook overfitting signature and the
reason train performance is never reported alone.

### Finding 3 - accuracy above the base rate still loses money

The best cell has validation accuracy **0.5136 against a drift base rate of
0.4972** - nominally +1.6 points of directional skill - and still loses.
Accuracy counts every bar equally; money does not. Being right on small moves
and wrong on large ones scores well on accuracy and badly at the bank. **This
vindicates the brief's insistence on trading metrics over accuracy**; a
project scored on accuracy would have called this cell a success.

### Finding 4 - the rotation null: selection alone beats the real result

The full 54-cell search was repeated 8 times on **circularly rotated training
labels**, which destroys any feature-label link while preserving the labels'
autocorrelation and drift.

| | best-of-54 validation net |
|---|---:|
| rotated labels (n=8) | mean **+146.2**, sd 198.2, max **+438.3** |
| **real labels** | **−39.6** |

**7 of 8 rotations beat the real result** (empirical p ≤ 0.889). Searching 54
cells on pure noise typically produces a *better* apparent result than the
real data does. Anyone reporting "best of 54" as a finding here would be
reporting less than nothing.

### Decision

No configuration advances. Test split remains sealed. Proceeding to R06
(walk-forward) because a single train/validation boundary can be unlucky, and
walk-forward is a required deliverable - **not** because the result is being
re-run in the hope of a better one. R06 changes the evaluation protocol, not
the model grid.

**Status: complete. NEGATIVE RESULT. No edge found.**

---

## R04 - Baselines

**Date** 2026-08-28
**Hypothesis** Not a model test. Establishes the bar any model must clear.
**Data** H1, k=8, train and validation. Test not read.
**Model** None - 10 mechanical rules.

### Result

| | train net | valid net | valid turnover |
|---|---:|---:|---:|
| always_long | +595.4 | −0.3 | 0.000 |
| long_vol_filtered | +604.1 | −11.7 | 0.025 |
| momentum_8 | −1,705.6 | −154.0 | 0.326 |
| momentum_1 | −7,254.9 | −1,591.4 | 1.034 |
| coin_flip | −5,929.9 | −1,436.5 | 0.991 |

**Turnover explains the ranking almost completely.** 0.00 → roughly flat;
0.33 → −$154; 1.00 → −$1,437. Every active baseline loses in proportion to
how often it trades.

**No naive signal beats drift.** Every momentum variant has accuracy *below*
the drift base rate on both splits. Mean reversion is above it on validation
(reversion_24: 0.5167 vs 0.4972) but still loses money.

**The bar for any model:** beat `always_long`'s **−$0.3** on validation with
accuracy above **0.4972**, at turnover low enough to survive. At an 8-hour
horizon that caps useful turnover near 0.125/bar.

### Bug found and fixed - a serious one, in my own instrument

The first run scored `always_long` at **−$6,753** on training while gold rose
**$522/oz** over exactly that period. Cause: `evaluate_positions` charged a
full spread on **every bar**, so a constant position paid 27,448 spreads
instead of one. Rewritten to charge cost on **turnover** -
`|Δposition| × spread / 2` - so a round trip costs one spread and holding
costs nothing.

**Third bug in four experiments that manufactured a false negative.** In this
project a broken instrument fails toward "nothing works", which is the
direction least likely to be questioned. Every future null must be checked
against a case whose answer is known independently - here, buy-and-hold
versus the actual price change.

**Status: complete.**

---

## R03 - Dataset construction and leakage proof

**Date** 2026-08-28
**Hypothesis** Not a hypothesis test. Builds the modelling table and proves
it is safe to fit on.
**Data** H1, k=8. **45,573 rows, 33 features.**
**Model** None.

### Integrity checks - all passed

1. **Mechanical lookahead test PASSED.** Features built on the first 4,000
   bars are bit-identical to the same features built with 500 future bars
   appended. Inspection cannot establish causality; appending data can. This
   is the check that would have caught the retired project's C3 leak.
2. **Purging.** Train→validation gap 58.0h, validation→test gap 10.0h, both
   exceeding the 8-hour label horizon. No label spans a boundary.
3. **Splits ordered and disjoint.**
4. **Target sanity** - see below.
5. **Feature health.** No column below 95% coverage, none degenerate, no pair
   above |r| = 0.98.

### Splits

| split | rows | independent | from | to |
|---|---:|---:|---|---|
| train | 27,448 | 3,431 | 2016-11-07 | 2021-07-30 |
| validation | 9,338 | 1,168 | 2021-08-02 | 2023-02-28 |
| test | 8,787 | 1,099 | 2023-03-01 | 2024-08-23 |

### Finding - the drift is not stable, and that is protective

| split | P(up) | mean abs move | median spread | required acc |
|---|---:|---:|---:|---:|
| train | 0.5151 | $5.09 | 0.360 | 0.5353 |
| **validation** | **0.4972** | $6.80 | 0.260 | 0.5191 |
| test | 0.5263 | $7.51 | 0.240 | 0.5160 |

Training carries upward drift; **validation carries none.** A model that
learns "be long" is therefore punished, not rewarded, by this validation set.
That is a fortunate property: the drift trap identified in R02 cannot be
cashed in here by accident. Spread also narrowed 0.36 → 0.24 over the years,
so the economic bar falls in later periods.

**Status: complete. No model has seen this data yet at time of writing.**

---

## R02 - Target and horizon research

**Date** 2026-08-28
**Hypothesis** Not a model test. Determines (a) what directional accuracy any
target would need to pay its costs, and (b) whether any structure exists at
all, using model-free tests so a null cannot be blamed on a bad model.
**Data** Post-hole M1 aggregated to M15/M30/H1/H4, **train split only**.
**Model** None.

### Finding 1 - the drift trap

**Gold rose +40.4% across the training period alone** (1292.10 → 1814.20).
At longer horizons the base rate of positive returns reaches 0.51-0.56.

The economic bar is `p* = 0.5 + spread / (2·E|move|)`. At H4 k=4, `p* =
0.5242` while the drift base rate is `0.5276`. **Buy-and-hold already clears
the cost bar at horizons of ~8 hours and beyond.**

So a "profitable backtest" is trivially obtainable by being permanently
long. **Every directional result must be scored against the drift base rate,
never against 50%.** Four of the twelve shortlisted cells show a *negative*
required edge - those are drift, not skill.

### Finding 2 - where the economics are reachable

| TF | k | E abs move | req. acc | drift | edge needed | indep. samples |
|---|---:|---:|---:|---:|---:|---:|
| H1 | 1 | 1.71 | 0.6054 | 0.5042 | **+0.1012** | 27,624 |
| H1 | 4 | 3.52 | 0.5512 | 0.5127 | +0.0385 | 6,905 |
| **H1** | **8** | **5.12** | **0.5352** | **0.5142** | **+0.0210** | **3,452** |
| H1 | 16 | 7.48 | 0.5241 | 0.5262 | −0.0022 | 1,725 |
| H4 | 1 | 3.40 | 0.5515 | 0.5101 | +0.0414 | 7,296 |
| H4 | 2 | 4.94 | 0.5354 | 0.5130 | +0.0225 | 3,647 |

At one-bar horizons the bar is brutal (H1 k=1 needs **60.5%** accuracy).
It falls steeply with horizon, but so does the independent sample count, and
past ~8 hours drift takes over.

### Finding 3 - structure exists at M15, and is probably microstructure

Lo-MacKinlay variance ratios (train only):

| TF | q=2 | q=4 | q=8 | q=16 | q=32 |
|---|---:|---:|---:|---:|---:|
| **M15** | **0.9713 (z=−3.68)** | **0.9525 (z=−3.36)** | **0.9465 (z=−2.51)** | 0.9529 (−1.58) | 0.9350 (−1.60) |
| M30 | 0.9809 (−1.90) | 0.9747 (−1.41) | 0.9803 (−0.73) | 0.9632 (−0.96) | 0.9491 (−0.98) |
| H1 | 0.9904 (−0.70) | 0.9988 (−0.05) | 0.9804 (−0.55) | 0.9618 (−0.76) | 0.9892 (−0.16) |
| H4 | 0.9916 (−0.39) | 0.9789 (−0.55) | 1.0098 (+0.16) | 1.0569 (+0.65) | 1.0491 (+0.40) |

**M15 rejects the random walk at q=2, 4 and 8** with VR < 1 - mean
reversion. Sign persistence is 0.4797, also below 0.5.

**This is almost certainly bid-ask bounce, not tradable structure.** VR < 1
at the shortest horizons combined with sub-0.5 sign persistence is the
classic microstructure signature: the price oscillates between bid and ask,
creating negative serial correlation that you cannot harvest because
capturing it means paying the very spread that produces it. M15 also carries
`cost/move = 0.568`. Recorded as detected-but-not-actionable, not as an edge.

At H1 and H4 nothing rejects the random walk.

### Decisions taken

1. **Primary timeframe H1, horizon k = 8 bars (8 hours).** Chosen because it
   balances the two binding constraints: required accuracy 0.5352 (reachable)
   against 3,452 non-overlapping training samples (enough to measure). M30
   k=16 and H4 k=2 are the same 8-hour economic horizon and give nearly
   identical numbers, confirming the horizon rather than the timeframe is
   what matters.
2. **Targets carried to R03:** 8-hour forward log return (regression) and its
   sign (classification).
3. **Mandatory baselines:** always-long (drift) and flat. A model is only
   interesting if it beats always-long on a risk-adjusted basis.
4. **M1 and M5 remain excluded** on cost grounds from R01.

### Bug found and fixed

The Lo-MacKinlay z-statistic was understated by a factor of √n - `delta_j`
already carries 1/n scaling through its squared denominator, and I multiplied
by `n` again. Every z printed as ≈0.00, which would have been reported as
"no structure anywhere". Corrected; M15 then rejected the random walk.
**Second instance in two experiments of a bug producing a plausible but wrong
null.**

**Status: complete. No edge claimed.**

---

## R01 - Data audit and objective timeframe selection

**Date** 2026-08-28
**Hypothesis** Not a hypothesis test. Establishes what the data supports,
before any target, feature or model exists, so the timeframe decision is not
inherited from the retired project (which assumed M1).
**Data** `data/raw/XAUUSD_M1.csv` - 2,747,158 bars, 2016-06-01 to 2024-08-23.
**Model** None.

### Findings

**A 133.4-day hole exists** (2016-06-24 09:48 → 2016-11-04 18:19). Usable
history starts after it: **2,723,669 M1 bars, 7.8 years**. Recorded in config
as `DATA_START = 2016-11-05` so no rolling window spans it.

**Transaction cost relative to a single bar's typical movement:**

| TF | bars | median abs move | spread | **cost / move** | AC(1) |
|---|---:|---:|---:|---:|---:|
| M1 | 2,747,158 | 0.1509 | 0.350 | **2.320** | −0.0199 |
| M5 | 550,824 | 0.3629 | 0.350 | **0.964** | −0.0247 |
| M15 | 184,409 | 0.6162 | 0.350 | 0.568 | −0.0183 |
| M30 | 92,254 | 0.8683 | 0.350 | 0.403 | −0.0109 |
| H1 | 46,171 | 1.2269 | 0.350 | 0.285 | −0.0052 |
| H4 | 12,152 | 2.5413 | 0.350 | 0.138 | +0.0052 |
| D1 | 2,032 | 7.6318 | 0.350 | 0.046 | +0.0137 |

**On M1 the spread is 2.3x a typical bar's entire move.** On M5 it is
0.96x - still roughly the whole bar. Any per-bar signal at those timeframes
must be enormous to pay for itself.

**Lag-1 autocorrelation is ~0 at every timeframe** (−0.025 to +0.014). No
linear serial structure in returns. This does not rule out non-linear or
conditional structure, which is what the ML work will test, but it removes
the simplest possible source of edge.

### Decisions taken

1. **`DATA_START = 2016-11-05`** - data quality, excludes the hole.
2. **Splits fixed at `TRAIN_END = 2021-08-01`, `VALID_END = 2023-03-01`** -
   the 60th and 80th percentiles of post-hole M1 bar count (60.3% / 80.8%),
   rounded to month starts. **Never to be moved.**
3. **Candidate timeframes carried forward: M15, M30, H1, H4.** M1 and M5 are
   excluded on cost grounds - not by habit, but
   because spread ≈ or exceeds a typical bar's move. D1 is retained only as
   a reference: 1,349 training bars is too few to fit anything non-trivial.

### Caveat recorded

`cost / move` compares spread to a **one-bar** move. A prediction horizon
spanning k bars scales the move by roughly √k, so timeframe and horizon
trade off against each other. The binding constraint is
`spread < predicted move over the horizon`, which R02 addresses directly.
Timeframe selection is therefore provisional until horizon is chosen.

### Bugs found and fixed during R01

* Loader assumed a tab-separated MT5 export; the actual schema is
  `time,open,high,low,close,tick_volume,spread,real_volume` (comma). Fixed.
* pandas 3.x returns `datetime64[us]`, not `[ns]`; dividing a raw int64 view
  by 1e6 produced timestamps in 1970. Fixed by converting through an
  explicit `datetime64[ms]`. **This produced a plausible-looking but entirely
  wrong first audit** - worth remembering as a class of error.

**Status: complete. No edge claimed, none sought yet.**
