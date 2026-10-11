# Finding 6 - cost is the binding constraint, and it disqualifies the equities

`cost_over_move` is one full quoted spread divided by the median one-bar move.
Above 1.0, a one-bar prediction cannot pay for itself at **any** accuracy.

| instrument | M1 | M5 |
|---|---:|---:|
| Volatility indices (25) | 0.24 - 0.83 | - |
| Volatility 250 (1s) | **2.83** | - |
| Boom (10) | 0.02 - 1.64 | - |
| XAUUSD | 0.756 | 0.381 |
| **AAPL.OQ** | **8.00** | 4.44 |
| **MSFT.OQ** | **14.00** | 7.00 |

**The two equities are arithmetically untradeable intraday on this venue.** A
40-point spread on AAPL against a 5-point median M1 move means eight typical
minutes of movement are consumed the instant the position opens; MSFT is
fourteen. No entry rule, filter or model changes that - the problem is on the
cost side of the inequality. These are CFDs on a synthetic-first broker, and
they are priced accordingly.

Gold at 0.756 (M1) is the cheapest real instrument here but still well above
the 0.285 measured for gold M1 on the previous broker, so Deriv is roughly
2.7× more expensive on gold.

The synthetics are the cheapest things on the venue relative to their own
movement - most sit at 0.24-0.51 on M1. That is a statement about ratio, not
about edge: cheap access to a martingale is still access to a martingale.

---

---
[All findings](../README.md)
