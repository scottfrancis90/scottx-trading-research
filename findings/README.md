# Findings index

Every test is reported, including the failures. Most results are **negative**: that is the point.
Each finding states the rule, the data, the control it was measured against, and the result in both halves of the history.

## Deriv synthetic indices (Boom, Crash, Volatility, Flip)

| # | Finding |
|---|---|
| 1 | [the synthetic/real divide is absolute](001-the-synthetic-real-divide-is-absolute.md) |
| 2 | [the Volatility indices are named after their volatility, exactly](002-the-volatility-indices-are-named-after-their-volatility-exactly.md) |
| 3 | [Boom and Crash are exact mirrors](003-boom-and-crash-are-exact-mirrors.md) |
| 4 | [what the N in "Boom N" actually is, and where the measurement fails](004-what-the-n-in-boom-n-actually-is-and-where-the-measurement-fails.md) |
| 5 | [no free drift anywhere](005-no-free-drift-anywhere.md) |
| 5b | [instrument age is the hidden variable, and it settles the drift question](005b-instrument-age-is-the-hidden-variable-and-it-settles-the-drift-questio.md) |
| 6 | [cost is the binding constraint, and it disqualifies the equities](006-cost-is-the-binding-constraint-and-it-disqualifies-the-equities.md) |
| 7 | [the real assets show the M1 bounce signature; the synthetics show nothing](007-the-real-assets-show-the-m1-bounce-signature-the-synthetics-show-nothi.md) |
| 8 | [the M30-and-up audit, and four instruments the study had never seen](008-the-m30-and-up-audit-and-four-instruments-the-study-had-never-seen.md) |
| 9 | [Crash Boom Flip: the mode is real, strongly detectable, and carries no direction](009-crash-boom-flip-the-mode-is-real-strongly-detectable-and-carries-no-di.md) |
| 10 | [the Gold RSI Tactical indices: levered gold, and an alpha that was a modelling artifact](010-the-gold-rsi-tactical-indices-levered-gold-and-an-alpha-that-was-a-mod.md) |
| 92 | [Boom/Crash replicates the null, and the outlier guard has a hole the size of the top 1%.](092-boom-crash-replicates-the-null-and-the-outlier-guard-has-a-hole-the-si.md) |

## High win rate, still losing: the win-rate trap

| # | Finding |
|---|---|
| 35 | [Is there a 90%-win scalp on gold in 2026? Yes, thirteen of them. All lose money, and none beats random entry.](035-is-there-a-90-win-scalp-on-gold-in-2026-yes-thirteen-of-them-all-lose-.md) |
| 60 | [The 12:00 UTC fade against the daily bias: 85% of trades reach the target and the rule loses 0.10 of a target per trade. The bias contributes nothing.](060-the-12-00-utc-fade-against-the-daily-bias-85-of-trades-reach-the-targe.md) |
| 61 | [An M5 sweep after 12:00 UTC against the daily bias at 1:2 wins 30% and needs 36%. Negative on 15 of 15 markets and 28 of 28 years.](061-an-m5-sweep-after-12-00-utc-against-the-daily-bias-at-1-2-wins-30-and-.md) |

## Costs, spread and execution

| # | Finding |
|---|---|
| 36 | [Can any entry reach +1R before -1R more than half the time? No. ~60,000 trades say 50%.](036-can-any-entry-reach-1r-before-1r-more-than-half-the-time-no-60-000-tra.md) |
| 39 | [Two supplied strategies tested. Both negative. Both for the same reason.](039-two-supplied-strategies-tested-both-negative-both-for-the-same-reason.md) |
| 40 | [Cross-asset lag scalp (gold vs DXY). The correlation is real and contemporaneous. No lag exists.](040-cross-asset-lag-scalp-gold-vs-dxy-the-correlation-is-real-and-contempo.md) |
| 41 | [Cost feasibility is necessary, not sufficient. Gold is the worst-cost instrument that works.](041-cost-feasibility-is-necessary-not-sufficient-gold-is-the-worst-cost-in.md) |

## Candlestick patterns and indicators

| # | Finding |
|---|---|
| 11 | [OHLC bar anatomy: shape says nothing, size says a lot](011-ohlc-bar-anatomy-shape-says-nothing-size-says-a-lot.md) |
| 12 | [Engulfing candlestick pattern. Pre-registered, universe-wide. NEGATIVE.](012-engulfing-candlestick-pattern-pre-registered-universe-wide-negative.md) |
| 13 | [Hammer / shooting star and pin bar. Same protocol. NEGATIVE.](013-hammer-shooting-star-and-pin-bar-same-protocol-negative.md) |
| 47 | [Bollinger squeeze breakout with volume confirmation. The filters genuinely work. They lift gross expectancy from negative to exactly zero, and cost is 5.5% of R.](047-bollinger-squeeze-breakout-with-volume-confirmation-the-filters-genuin.md) |
| 65 | [FxWirePro's technical layer: nothing survives. The SMA filter that looked strongest fails on the one pair we still trade.](065-fxwirepro-s-technical-layer-nothing-survives-the-sma-filter-that-looke.md) |
| 116 | [Two-RSI rule (RSI14 vs RSI35) on 17 forex pairs: no edge (2026-10-04)](116-two-rsi-rule-rsi14-vs-rsi35-on-17-forex-pairs-no-edge-2026-10-04.md) |
| 117 | ["Both RSIs drop to a level" (separate panels, not a cross) (2026-10-04)](117-both-rsis-drop-to-a-level-separate-panels-not-a-cross-2026-10-04.md) |
| 118 | [Untouched test of Finding 117 on 11 new pairs: FAIL (2026-10-05)](118-untouched-test-of-finding-117-on-11-new-pairs-fail-2026-10-05.md) |

## Smart Money Concepts: ICT order blocks, FVG, CRT, liquidity

| # | Finding |
|---|---|
| 66 | [Candle Range Theory (3-candle sweep): the pattern hits at exactly its own break-even rate, and its mirror does no worse.](066-candle-range-theory-3-candle-sweep-the-pattern-hits-at-exactly-its-own.md) |
| 67 | [Candle Range Theory, the full study: the setups are statistically indistinguishable from random entries, and every knob only moves the loss closer to zero from below.](067-candle-range-theory-the-full-study-the-setups-are-statistically-indist.md) |
| 68 | [CRT top-down (higher-timeframe range, H4 entry): nothing survives, and two bugs of mine had to be removed first.](068-crt-top-down-higher-timeframe-range-h4-entry-nothing-survives-and-two-.md) |
| 89 | [the level-to-level liquidity run: positive on daily, gone on H4 where the sample is seven times larger.](089-the-level-to-level-liquidity-run-positive-on-daily-gone-on-h4-where-th.md) |
| 90 | [correction to Finding 89: the retrace IS the entry. Re-measured, the trades get fair odds and nothing more.](090-correction-to-finding-89-the-retrace-is-the-entry-re-measured-the-trad.md) |
| 91 | [the high reward:risk "excess" was degenerate stops. With a minimum-R floor the effect flips sign between splits.](091-the-high-reward-risk-excess-was-degenerate-stops-with-a-minimum-r-floo.md) |
| 121 | [Break -> sweep -> sweep -> entry (H1, user's sequence): no edge (2026-10-06)](121-break-sweep-sweep-entry-h1-user-s-sequence-no-edge-2026-10-06.md) |
| 122 | [The Aristotle Bible (AISB), Vols I/II/III/V as written: no edge (2026-10-06)](122-the-aristotle-bible-aisb-vols-i-ii-iii-v-as-written-no-edge-2026-10-06.md) |
| 123 | [Aristotle Bible Vol VII (Asia Directional Rule): no edge (2026-10-06)](123-aristotle-bible-vol-vii-asia-directional-rule-no-edge-2026-10-06.md) |
| 126 | [ICT POIs: order block, FVG, breaker, premium/discount - no edge (2026-10-06)](126-ict-pois-order-block-fvg-breaker-premium-discount-no-edge-2026-10-06.md) |
| 128 | [Daily FVG/OB, enter WHEN IT APPEARS (no retest): no edge (2026-10-07)](128-daily-fvg-ob-enter-when-it-appears-no-retest-no-edge-2026-10-07.md) |
| 129 | [Daily order block, "bullish OB enter, bearish OB enter" (at formation): no edge (2026-10-07)](129-daily-order-block-bullish-ob-enter-bearish-ob-enter-at-formation-no-ed.md) |
| 130 | [H1 OB "rejects 3 times in a downtrend": a random zone does the same (2026-10-08)](130-h1-ob-rejects-3-times-in-a-downtrend-a-random-zone-does-the-same-2026-.md) |
| 131 | [H1 OB at the RECENT HIGH, newest only, every rejection: 1st touch small edge, 2nd none (2026-10-08)](131-h1-ob-at-the-recent-high-newest-only-every-rejection-1st-touch-small-e.md) |
| 132 | [Recent-high OB rule on H4 and DAILY: no edge (2026-10-08)](132-recent-high-ob-rule-on-h4-and-daily-no-edge-2026-10-08.md) |
| 133 | ["An OB formed with liquidity is real": H1 no; H4 a fragile hint (2026-10-08)](133-an-ob-formed-with-liquidity-is-real-h1-no-h4-a-fragile-hint-2026-10-08.md) |
| 134 | [M30 OB formed in the LONDON window: better than other OBs; with liquidity ~break-even (2026-10-08)](134-m30-ob-formed-in-the-london-window-better-than-other-obs-with-liquidit.md) |
| 135 | [London OB targeting the opposite Asia OB (M30): too rare to judge (2026-10-08)](135-london-ob-targeting-the-opposite-asia-ob-m30-too-rare-to-judge-2026-10.md) |
| 138 | [Daily: liquidity grab inside a same-direction OB/breaker: no edge (2026-10-08)](138-daily-liquidity-grab-inside-a-same-direction-ob-breaker-no-edge-2026-1.md) |
| 142 | [FX H4 break -> pullback -> rejection -> continuation (user's pattern): no edge (2026-10-09)](142-fx-h4-break-pullback-rejection-continuation-user-s-pattern-no-edge-202.md) |
| 143 | [FX: the first order block of the day / from London does not set the day's direction (2026-10-09)](143-fx-the-first-order-block-of-the-day-from-london-does-not-set-the-day-s.md) |
| 144 | [First London OB, lock in a small profit (M30, 28 pairs): no edge (2026-10-09)](144-first-london-ob-lock-in-a-small-profit-m30-28-pairs-no-edge-2026-10-09.md) |

## Strategy Factory: genetic algorithm search and the bugs it caught

| # | Finding |
|---|---|
| 74 | [the gold Strategy Factory: seven runs, 62.7 million genomes, zero survivors, and one shape it will not stop finding.](074-the-gold-strategy-factory-seven-runs-62-7-million-genomes-zero-survivo.md) |
| 75 | [the gold factory produced a survivor, and it passed a pre-registered holdout.](075-the-gold-factory-produced-a-survivor-and-it-passed-a-pre-registered-ho.md) |
| 76 | [the GA survivor's losers run deep into profit first, and that fact is useless](076-the-ga-survivor-s-losers-run-deep-into-profit-first-and-that-fact-is-u.md) |
| 77 | [the GA survivor was lookahead in the signal generator. Findings 75 and 76 are withdrawn.](077-the-ga-survivor-was-lookahead-in-the-signal-generator-findings-75-and-.md) |
| 78 | [the user's four corrections, measured. The exits were never the problem; the entry is a coin flip.](078-the-user-s-four-corrections-measured-the-exits-were-never-the-problem-.md) |
| 80 | [the GA was given sand and asked to build a house. It now has bricks.](080-the-ga-was-given-sand-and-asked-to-build-a-house-it-now-has-bricks.md) |
| 81 | [the molecules run: no survivors, and a total collapse the detector did not catch.](081-the-molecules-run-no-survivors-and-a-total-collapse-the-detector-did-n.md) |
| 82 | [the molecules-only run: no survivors, and the context gene was doing nothing at all.](082-the-molecules-only-run-no-survivors-and-the-context-gene-was-doing-not.md) |
| 83 | [defect 12: overlapping pending orders were filling in signal order, not time order. And the engine's own reproduction test was running the wrong rule.](083-defect-12-overlapping-pending-orders-were-filling-in-signal-order-not-.md) |
| 84 | [the two-stage entry built and searched. Negative, and my own lowered floor manufactured the false positive.](084-the-two-stage-entry-built-and-searched-negative-and-my-own-lowered-flo.md) |
| 85 | [the chapter method on FX: negative on 17 pairs, and the mirror loses too.](085-the-chapter-method-on-fx-negative-on-17-pairs-and-the-mirror-loses-too.md) |
| 86 | [the factory on FX: 8,649 genomes, 17 pairs, H4 and D1. Nothing, and nothing fake either.](086-the-factory-on-fx-8-649-genomes-17-pairs-h4-and-d1-nothing-and-nothing.md) |
| 136 | [GA restored with SMC genes; first run: COLLAPSE, no survivors; factory defects 15-16 (2026-10-08)](136-ga-restored-with-smc-genes-first-run-collapse-no-survivors-factory-def.md) |
| 137 | [GA rerun (seed 12) with defects 15-16 fixed and Asia/opposite-OB genes: no survivors (2026-10-08)](137-ga-rerun-seed-12-with-defects-15-16-fixed-and-asia-opposite-ob-genes-n.md) |
| 139 | ["Math" EA study (user's plan, pre-registered ml/math_prereg.md): no edge by the rule; one lead (2026-10-09)](139-math-ea-study-user-s-plan-pre-registered-ml-math-prereg-md-no-edge-by-.md) |
| 140 | [GA over the "Math" setup: overfit, every top genome loses on unseen years (2026-10-09)](140-ga-over-the-math-setup-overfit-every-top-genome-loses-on-unseen-years-.md) |

## Trade management

| # | Finding |
|---|---|
| 87 | [there is no "risk-free" entry candle. Every type goes 1.4 ATR underwater first.](087-there-is-no-risk-free-entry-candle-every-type-goes-1-4-atr-underwater-.md) |

## Infrastructure

| # | Finding |
|---|---|
| 93 | [overnight queue halted: Smart App Control blocked every parquet engine.](093-overnight-queue-halted-smart-app-control-blocked-every-parquet-engine.md) |

## Study notes

- [The universe, and what came back](notes/the-universe-and-what-came-back.md)
- [Limitations](notes/limitations.md)
- [Not yet done](notes/not-yet-done.md)
- [CORRECTION - 2026-08-31: the "100,000-bar terminal cap" did not exist](notes/correction-2026-08-31-the-100-000-bar-terminal-cap-did-not-exist.md)
- [CORRECTION - 2026-08-31: costs used TODAY's spread across 10-17 years](notes/correction-2026-08-31-costs-used-today-s-spread-across-10-17-years.md)
- [METHODS - `deriv_study/audit.py`: the four guardrails, now enforced in code](notes/methods-deriv-study-audit-py-the-four-guardrails-now-enforced-in-code.md)
