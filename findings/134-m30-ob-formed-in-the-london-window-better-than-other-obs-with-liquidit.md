# Finding 134 - M30 OB formed in the LONDON window: better than other OBs; with liquidity ~break-even (2026-10-08)

ml/ob_london.py (trades ml/ob_london_trades.csv). Recent-extreme OB on gold M30
2004-2026 (24,929 OBs; 3,666 with the extreme in 02:00-05:00 NY). First return,
stop beyond extreme + $0.25 (median $3.95, cost 9% of R), cap 8h, vs random.
  London OBs, any:      n 926  edge 1R +0.044 / 2R +0.057 (DEV +0.04, VAL +0.08)  net -0.05/-0.02
  London OBs WITH liq:  n 291  2R edge +0.105 (DEV +0.066, VAL +0.164)  net +0.012 R
  other-time OBs, any:  n 5,237 edge 0.000 / +0.010
  other-time WITH liq:  n 1,310 2R edge +0.056 (t 2.0); bullish WITH +0.100 (t 2.5)
  WITHOUT liquidity, other times: -0.011 / -0.006.
Both factors point the same way in both halves on M30 (London > other times;
liquidity > none), agreeing with the H4 hint (F133) though H1 disagreed. Best cell
(London + liquidity, 2R) is ~break-even after cost, ~13 trades/yr. Small, real-
looking, not yet worth money.

---
[All findings](../README.md)
