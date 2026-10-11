# Finding 93 - overnight queue halted: Smart App Control blocked every parquet engine.

*2026-09-28. Not a market finding. An environment failure that stops all work.*

Between the Boom/Crash run (Finding 92) and the next item twenty minutes later,
Smart App Control blocked:

* `pyarrow/_parquet.pyd` - "An Application Control policy has blocked this file"
* `fastparquet/speedups.pyd` - same
* the `polars` binary - "Polars binary is missing!"

`pandas.read_parquet` therefore fails, `factory.data.load()` raises, and the GA,
every backtest and all of `deriv_study/` are inoperable. Reinstalling does not
help: pip reports the requirement already satisfied and SAC re-blocks the
freshly written .pyd.

**Queue status: item 1 complete (Finding 92). Items 2 and 3 cannot run -
both require parquet.**

Item 2 could technically be done from `data/raw/XAUUSD_M15.csv`, but that is a
DIFFERENT broker whose history stops in 2024, so the numbers would not be
comparable to anything already recorded. Producing a non-comparable figure and
filing it as the answer would be worse than reporting the blocker.

This is the second time SAC has stopped this project (it killed the Deriv bot on
2026-09-04). The fix is the user's: Windows Security -> App & browser control ->
Smart App Control -> Off, which cannot be undone without a Windows reset.

---
[All findings](../README.md)
