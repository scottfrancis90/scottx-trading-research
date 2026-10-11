# Finding 135 - London OB targeting the opposite Asia OB (M30): too rare to judge (2026-10-08)

ml/ob_asia_london.py. Sell the first return to a London-formed bearish OB when a
bullish Asia-formed OB (same day, alive) sits below; target its top. Mirror buys.
Only 52 setups in 22 years (~2/yr). Target is close: median 0.3R -> win 71%,
+0.049 R net, edge vs random (same stop/target) +0.139 (t 1.8; DEV +0.09, VAL
+0.17). Sells 29: win 79%, +0.105 R, edge +0.21 (t 1.9). H4 bias agreement does
not help (n 21, edge +0.006). Same trades with a 2R target: +0.104 R. Direction
consistent, sample far too small. To be added to the GA as an Asia-formation
option and an opposite-OB target after the running search finishes.

---
[All findings](../README.md)
