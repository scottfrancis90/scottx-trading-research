# Finding 7 - the real assets show the M1 bounce signature; the synthetics show nothing

| symbol | AC(1) z | VR(2) | VR(2) z | VR(8) z |
|---|---:|---:|---:|---:|
| AAPL.OQ M1 | **−10.11** | 0.968 | **−3.54** | −2.60 |
| MSFT.OQ M1 | **−7.69** | 0.976 | −1.72 | −0.21 |
| XAUUSD M1 | **−8.09** | 0.974 | **−3.82** | −2.44 |

All three real instruments reject the random walk at M1 with VR < 1 and
negative first-order autocorrelation - mean reversion at the shortest horizon.

This is the bid-ask bounce, and it is **not harvestable**: capturing it requires
paying the spread that creates it, and Finding 6 gives the size of that spread.
The gold project reached the identical conclusion at M15 on a different broker
and a different decade of data; seeing it reproduce at M1 on Deriv is
confirmation of the mechanism, not the discovery of an edge. Recorded as
detected-but-not-actionable.

Against that, **0 of 135 serial-structure z-scores across the 45 synthetics
exceed |2|**, where independent tests would produce about 7. The synthetics are
random walks at every horizon tested (q = 2, 4, 8, 16, 32). The count being
*below* chance rather than at it says the three statistics per symbol are
strongly correlated with one another and the robust z is conservative in finite
samples - so read this as "no structure, robustly", not as a calibrated p-value.

---

---
[All findings](../README.md)
