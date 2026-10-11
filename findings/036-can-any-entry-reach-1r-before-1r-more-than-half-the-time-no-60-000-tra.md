# Finding 36 - Can any entry reach +1R before -1R more than half the time? No. ~60,000 trades say 50%.

Direct follow-up to Finding 35, and an answer to a question asked plainly:
make every trade reach 1:1 before its stop.

### It is a barrier problem, not a strategy problem

With a symmetric bracket the stop IS 1R, so "does it reach +1R before -1R"
asks which of two equidistant barriers price touches first. On a
near-martingale that is a coin flip, and no choice of entry moves it. The
only lever that raises the number is moving the target closer than the stop,
which is the structure Finding 35 priced at $5,000 -> $494.

A 36-cell sweep on 2026 gold (6 families x 3 stop widths x M30/H1) landed
entirely between 42.4% and 56.4%. **Random entry spanned 45.7% to 55.1% -
the same band.** BRK 56.4% and FADE 43.6% sum to 100 because they are one
signal with the sign flipped, which is the internal check that the
measurement is sound.

### The one candidate, pre-registered and then killed

Breakout sat above the null in every 2026 cell: 50.9 / 54.6 / 55.8 on M30,
52.5 / 56.4 / 56.4 on H1. The best was 54.6% on n = 740, about 2.5 SE above
the coin flip - which at 36 draws is roughly what chance delivers. Frozen
exactly as found (20-bar breakout, +/- 1R, R = 2 x ATR(14), 400-bar horizon,
same-bar touch scored a loss) and tested with the pass condition fixed
first.

**(a) Gold M30 2018-2025 - the years that did not find it**

    n 9,991 | +1R first 49.7% | net -0.0351 R | total -350.7 R      FAIL

    year        n   +1R first     net R
    2018     1223      48.0%    -0.0916
    2019     1274      49.5%    -0.0573
    2020     1089      50.7%    -0.0085
    2021     1229      49.2%    -0.0432
    2022     1277      50.2%    -0.0214
    2023     1260      48.3%    -0.0621
    2024     1281      48.8%    -0.0445
    2025     1358      52.8%    +0.0436
    years positive: 1 of 8

H1, same parameters: 49.5%, net -0.0281 R, 3 of 8 years. FAIL.

**(b) Seven non-gold instruments, M30, 2018-2026**

    AUDJPY          11884   49.3%   -0.1025
    BTCUSD          11716   48.8%   -0.1306
    Germany 40       3496   52.1%   +0.0237
    Wall Street 30   3633   50.2%   -0.0199
    US Oil           3706   48.7%   -0.0649
    UK Brent Oil     3446   48.5%   -0.0730
    SOLUSD           7782   50.3%   -0.1340

    net positive on 1 of 7                                          FAIL

### Verdict

**Both criteria failed.** The 54.6% that produced the candidate does not
appear in any of the eight prior gold years or in six of the seven other
instruments. It was 2026 noise, and this is the third time in this document
that a champion selected on recent data has evaporated on contact with the
rest (Finding 34's chase test, the 6R exit at 4/7, and now this).

Pooled across gold M30, gold H1 and seven instruments - roughly **60,000
trades** - the rate at which price reaches +1R before -1R is **48.5% to
52.1%, centred on 50%**, whatever the entry, stop width, timeframe or
instrument.

There is no entry rule in this study that makes trades reach 1:1 first. The
number is a property of the barriers, not of the signal. This is Finding 32
(direction unpredictable, corr +0.006) arriving from a second direction, and
it is why the straddle declines to pick a side at all.

Script: `info/brk11.py`.

---

---
[All findings](../README.md)
