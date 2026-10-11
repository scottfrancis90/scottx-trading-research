# Finding 47 - Bollinger squeeze breakout with volume confirmation. The filters genuinely work. They lift gross expectancy from negative to exactly zero, and cost is 5.5% of R.

**Pre-registered before running**, frozen at `artifacts/prereg_squeeze_breakout.json`.
Not a repeat: Finding 20 enters on volatility ALREADY HIGH, this enters on
compression - the opposite sign - and `tick_volume` had never been used as a
filter anywhere in this study.

**Rules, textbook values, nothing swept.** Bollinger(20, 2.0); bandwidth
(upper-lower)/mid; squeeze = bandwidth in the bottom 20% of its trailing
100-bar rank; breakout = close beyond the prior 20-bar extreme; volume =
breakout bar `tick_volume` > 1.5x its trailing 20-bar median; **entry at the
NEXT bar's open**, since the signal is a close; stop 2N (N = ATR20); exit on
the trailing 10-bar opposite extreme, the stop, or 100 bars. Provenance gate,
gap-honest fills and multiplicity correction from `audit.py` all applied.
16 markets: 14 Deriv forex H1 pairs plus XAUUSD M30 and H1.

**The 2x2 control**, because "more selective than Donchian" is a comparative
claim that a bare backtest cannot answer:

| book | trades | mean R | win% | mean t | mean t_OOS | mean t_short |
|---|---|---|---|---|---|---|
| squeeze+volume | 28,207 | **-0.0631** | 33.3% | -1.82 | -1.85 | -1.34 |
| squeeze only | 45,147 | -0.0726 | 32.4% | -2.75 | -2.12 | -1.89 |
| volume only | 61,031 | -0.0629 | 34.1% | -2.82 | -2.64 | -2.03 |
| bare breakout | 89,840 | -0.0821 | 32.6% | -4.65 | -3.41 | -3.22 |

**The filters are real.** Every ordering runs the right way: both filters beat
one, one beats none. Trade count falls 69% and mean R improves by +0.019 R.
The hypothesis that a squeeze is more selective than a generic Donchian is
**supported**. The claim of a higher win rate is **not** - 33.3% against
32.6%, a difference of 0.7 points, on a structure whose exit design makes it
trend-following (low hit rate, fat right tail) whatever the entry filter.

**The decisive split - cost or signal?** Re-running identical trades with
spread and slippage removed:

| book | net mean R | gross mean R | cost/trade |
|---|---|---|---|
| squeeze+volume | -0.0631 | **-0.0080** | 0.0552 |
| squeeze only | -0.0726 | -0.0188 | 0.0538 |
| volume only | -0.0629 | -0.0107 | 0.0522 |
| bare breakout | -0.0821 | -0.0314 | 0.0507 |

Gross -0.0080 R on 28,207 trades is **statistically zero** (SE ~0.007,
t ~ -1.1). So the filters do exactly what was claimed for them - they take
gross expectancy from reliably negative (-0.0314) to indistinguishable from
zero - and that is the ceiling. Zero is not a business. To be viable, gross
would have to exceed **0.055 R**, and it is at 0.000.

**A reading trap in the corrected table.** Seven markets "survive Bonferroni
or BH" out of sample. Every one of them has a NEGATIVE t: EURGBP -4.61,
EURCHF -3.35, GBPJPY -2.77, GBPAUD -2.74, AUDUSD -2.65, XAUUSD M30 -2.51,
USDCHF -2.49. They are significant **losses**, not wins. The only positive
out-of-sample t in the book is XAUUSD H1 at +1.23, which is not significant.

**Conclusion.** Eleventh negative, and the most instructive one. Previous
negatives died because the entries carried no information. This one has
entries that are measurably better than the unfiltered baseline - the idea
has merit - and it still fails, because "better than negative" turned out to
mean "zero", and zero cannot pay a 5.5%-of-R toll. Selectivity improves the
signal; it does not create one.

---

---
[All findings](../README.md)
