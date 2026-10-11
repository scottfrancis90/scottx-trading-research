# Limitations

* **Short window.** M1 covers 69 days for the synthetics and ~104 for the real
  assets. That is ample for a stationary generator and thin for a real market;
  no claim here about gold or the equities should be read as a multi-year
  result. The H1 pass (synthetics back to 2019, XAUUSD to 2011) is what would
  settle stability across years, and it has not been run.
* **Multiple testing.** 48 symbols × ~20 statistics. Isolated significant
  values are expected and none is treated as a finding on its own. The claims
  above rest on effects that hold across an entire group or separate two groups
  with no overlap.
* **Market closed.** 2026-08-30 is a Sunday. Quoted spreads for XAUUSD, AAPL
  and MSFT are weekend quotes and may not be the spreads paid in session -
  Finding 6 needs re-measuring on a live Monday before it is treated as final.
  The synthetics trade 24/7 and are unaffected.
* **The jump detector under-counts frequent small spikes** - see Finding 4.
  Boom/Crash below N = 300 are not properly characterised by this pass.
* **Two equities is not a sample of equities.** AAPL and MSFT were chosen for
  liquidity and recognition, and nothing here generalises to Deriv's other 447.

---
[All findings](../../README.md)
