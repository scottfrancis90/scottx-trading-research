# CORRECTION - 2026-08-31: the "100,000-bar terminal cap" did not exist

Several findings above refer to a 100,000-bar history ceiling and attribute
it to the MT5 terminal. **That was wrong.** The terminal setting
(`common.ini [Charts] MaxBars`) was already 100,000,000. The cap was
`MAX_BARS = 100_000` in `deriv_study/config.py`, handed directly to
`copy_rates_from_pos`, so every request returned exactly 100,000 bars and the
round number was mistaken for a broker or terminal limit.

Measured immediately after raising it:

| series | as fetched under the cap | actually available |
|---|---|---|
| XAUUSD M30 | 100,000 - from 2018-03-02 | **183,015 - from 2011-01-02** |
| XAUUSD M1 | 100,000 - 69 days | **5,448,564 - from 2011-01-02** |
| Boom 600 M1 | 100,000 - 69 days | **1,051,834 - from 2024-08-30** |

### What this invalidates

* **Any claim that M1 or M5 hold the SHORTEST history on the venue.**
  Withdrawn. XAUUSD M1 reaches 2011. The case for working at M30 and above
  rests on COST alone, which is unaffected and remains strong: spread costs
  0.30 R at M1 versus 0.024 R at M30 on Boom 600.
* **Finding 5b's remark that M30 "is still hitting the terminal's ceiling".**
  It was hitting mine.
* **The M1-versus-M30 comparison on the EMA-confirmed setup**, which argued
  M1 was a 69-day sample against M30's 730 days. Boom 600 M1 covers the same
  730 days. The other two arguments there - the two timeframes disagreeing
  (corr +0.06) and M1 costing 0.30 R - stand unchanged.

### What it does NOT invalidate

* **Instrument inception dates (Finding 5b).** Those came from D1 and H4
  series, which were far below the cap and therefore untruncated.
* **Every cost, win-rate, breakeven and mirror result.** Those were measured
  on the data actually held; more data changes precision, not the arithmetic.
* **Finding 16's rejection of the stop-width hypothesis.** The reasoning for
  why XAUUSD H1 2011-2018 was held out was wrong (M30 also reaches 2011), but
  the data genuinely had not been used, so the test was valid.

Fixed in `config.py` with a comment explaining why the value must not be
rounded back down. Affected series re-fetched.

---

---
[All findings](../../README.md)
