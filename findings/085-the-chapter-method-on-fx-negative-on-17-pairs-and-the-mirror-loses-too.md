# Finding 85 - the chapter method on FX: negative on 17 pairs, and the mirror loses too.

*2026-09-27. The GOLD spec applied UNCHANGED to FX. Nothing refitted. Per pair
50% train / 25% validate; the last 25% was not read.*

At the user's instruction after gold came back negative: *"test it on fx but you
kwn with good analysis fx is good always so now we move all to fx"*.

### First, a scale fact that decided which timeframe could even be tested

The method's stop is the rejection candle's extreme -- its size is set by the
market, not chosen. Measured:

| | median R, in spreads |
|---|---|
| FX M30 | **1.4 - 3.3** |
| FX H1 | 1.8 - 5.4 |
| FX H4 | 6.8 - 12.8 |
| GOLD H1 | 12 - 14 |

At 2 spreads the cost is half the risk on every trade. **The method's defining
virtue -- "good entry give you good SL" -- is what makes it untradeable on FX
intraday.** The same rejection candle that gives a healthy stop on gold sits
inside the spread on EURUSD, because FX bars are far smaller in percentage
terms while spreads are not. H4 is the first FX timeframe where the stop clears
the spread, and H4 was built from the H1 files by CALENDAR resampling so all 17
pairs were available rather than the 4 on disk.

### Result: negative on both splits, all four rejection definitions

| rejection | TRAIN pooled | VALIDATE pooled | pairs positive |
|---|---|---|---|
| close_back | -0.0943 (t -1.38) | **-0.2651** (t -2.63) | 4/17, 5/17 |
| displace | -0.1140 (t -1.45) | **-0.1845** (t -1.65) | 5/17, 7/17 |
| wick | -0.1002 (t -1.18) | **-0.2453** (t -1.89) | 6/16, 4/16 |
| engulf | -0.0974 (t -0.75) | -0.0994 (t -0.58) | 7/15, 6/15 |

Fewer than half the pairs positive on every mode. That is noise scattered
around a negative mean, which is what a cost with no edge behind it looks like.

### And the mirror loses as well

The user's fallback: *"if still negative then we go with the mirror the beat the
rule since we depend on what is working"*. Same trades, direction flipped:

| rejection | TRAIN rule / mirror | VALIDATE rule / mirror |
|---|---|---|
| close_back | -0.0943 / **-0.1884** | -0.2651 / -0.0445 |
| displace | -0.1140 / **-0.1750** | -0.1845 / -0.0313 |
| wick | -0.1109 / **-0.1902** | -0.2453 / -0.0397 |
| engulf | +0.0072 / **-0.1249** | -0.0994 / +0.0615 |

**Both directions lose on TRAIN in all four modes**, and the mirror is still
negative on validate in three of four. This is the general lesson and it is
worth stating plainly:

> A losing rule does not imply a winning mirror. When both sides lose by about
> the cost, there is no directional information at all and the mirror simply
> pays the spread in the other direction.

The same was true on gold: the three M30 cells where the rule lost on both
splits had mirrors at -0.21, -0.28 and -0.27 on train.

### "FX is good always" -- tested

Not for this method, and the reason is mechanical rather than a matter of
analysis quality. This project's FX record already cut both ways: Findings
48/49 validated the Asian-range straddle on GBPJPY, USDJPY and GBPUSD, while
Finding 61 was negative on 15 of 15 markets. Seventeen pairs is a real
cross-section, and it says no.

**Status: the two-stage chapter method is negative on gold and on 17 FX pairs.
Nothing built, no money risked, every holdout still clean.**

---

---
[All findings](../README.md)
