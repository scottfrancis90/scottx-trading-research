# Finding 138 - Daily: liquidity grab inside a same-direction OB/breaker: no edge (2026-10-08)

ml/liq_in_ob_daily.py. Gold daily 2004-2026: 251 LiquidityX grabs, 568 OBs
(indicator definition, swing 2) + breakers. Grab candle's wick inside a live
zone of the same direction -> trade the reversal next open; stop beyond zone/wick
+ $0.25; 1R/2R; 20d cap; random control. No grab ever fell only inside an
OPPOSITE zone (the skip rule never fired).
Inside same-side OB: n 131 (5.8/yr), 1R edge -0.042, 2R -0.009 (both halves ~0).
Inside same-side breaker: n 57 (2.5/yr), 1R +0.094 (t 0.8), 2R +0.012; sells 2R
+0.255 (n 30, t 1.3). Outside any zone: n 58, 1R +0.116 (DEV +0.40 / VAL -0.28).
Too few daily grabs to judge; nothing separates from random.

---
[All findings](../README.md)
