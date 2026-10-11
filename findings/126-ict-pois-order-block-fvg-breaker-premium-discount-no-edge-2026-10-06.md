# Finding 126 - ICT POIs: order block, FVG, breaker, premium/discount - no edge (2026-10-06)

ml/poi.py (output ml/poi_out.txt). Gold M30 and M15 2004-2026. Standard
definitions fixed before the run: FVG >= 0.2 ATR14; OB = last opposite candle
(within 5) before the FVG move; breaker = OB closed through, flipped; P/D =
previous-day 50%. Entry = first retest that closes back out in direction, next
open, 02:00-16:00 NY; stop beyond zone + $0.25; 1R / 2R; flat 16:30 NY; $0.35.
78k zones (M30) / 159k (M15). Every arm loses net (-0.07 to -0.20 R) and sits on
the random-entry control: FVG +/-0.01, breaker -0.04..+0.02, P/D no consistent
help. Only M30 order block (no P/D, 1R) beats random in both halves: +0.030
(t 1.8) / +0.027 (t 1.7) -> ~$0.05/trade vs $0.35 cost; M15 OB fails in VAL.
Zones drawn on tradingview/LondonSweep.pine as a map, not as signals.

---
[All findings](../README.md)
