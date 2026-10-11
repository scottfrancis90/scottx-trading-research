# METHODS - `deriv_study/audit.py`: the four guardrails, now enforced in code

Findings 42-46 were each nearly a false positive. The checks that caught them
are now a module rather than a lesson, so the next result has to clear them
before it is believed. `python -m deriv_study.audit` self-tests all five
against the exact cases that caught us.

**1. `validate_data(df, name)`** - returns a `DataReport` with `.ok`,
`.problems`, `.warnings`, `.suggested_start`. Checks duplicate and
non-increasing timestamps, intra-week gaps (as a fraction, so weekend holes
do not spam), OHLC containment, non-positive prices, zero-range rate, the
longest consecutive flat run, and >10x price-scale splices.

Two separate provenance traps, because one heuristic does not find both:

  * *flat bars* find pegged and dead feeds. USDJPY/USDCHF fail on 2.3%
    zero-range and a 3,515-bar flat run; the per-year rate gives a cut date.
  * *inception dates* find what flat bars cannot. A vendor reconstruction of
    EURUSD from the DEM basket has perfectly normal ranges, so the flat-rate
    cut lands at **1990** - nine years before the euro existed. `INCEPTION`
    encodes 1999-01-04 for anything EUR-crossed, which also catches EURJPY
    (data from 1993), EURCHF, EURGBP, EURAUD, EURCAD. `FLOAT_ERA` flags
    pre-1973 Bretton Woods pegs.

**2. `entry_fill()` / `exit_fill()`** - gap-honest stop-order fills. A
buy-stop at 100.0 on a bar that opened at 102.0 fills at **102.0**; a long's
protective stop at 95.0 on a bar that gapped to 92.0 fills at **92.0**.
Filling at the level regardless of gaps is what moved gold M30 from t=-0.62
to t=+2.39 in Finding 42.

**3. `PreRegistration`** - dataclass carrying hypothesis, prediction, entry,
exit, risk, markets, timeframes, params. `freeze()` writes it with a sha256;
`verify()` on a later run **raises** if any field changed, naming the edited
fields. "Do not curve-fit after seeing results" becomes something the code
enforces rather than something we promise.

**4. `MultipleTests`** - `.add(name, p)`, then `.report()` prints raw,
Bonferroni and Benjamini-Hochberg adjusted p side by side. `.note_dependence()`
records non-independence and prints the standing warning that **neither
correction fixes dependence** - the trap in Finding 46, where five events were
four correlated bars in one 24-hour episode.

**5. `account_forensics(deals, bar_minutes=...)`** - magic-number
distribution, promotional comment tags, missing SL/TP, lag from bar close
(with a z against uniform), and local-hour histogram. On a third-party account's deals it
reproduces the whole Finding 44/45 read unaided: 5/5 magic zero, promotional
tag flagged, 5/5 with no stop, mean lag 3.40 min (z = -2.12) with the verdict
"far too slow for an EA firing on bar close".

**Wired into the pipeline, not just available.** `info/pyramid_fx.py` now
calls `validate_data` per pair and cuts to `suggested_start` before testing.
Re-running Finding 43 through the automatic gate reproduces the manual result
- mean t -0.84 pyramid / -0.70 single, **0 of 14 pairs with short-side skill**
- confirming the gate matches the hand-applied 1999 cut it replaces.

---

---
[All findings](../../README.md)
