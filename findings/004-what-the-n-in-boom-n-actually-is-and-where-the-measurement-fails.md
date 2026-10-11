# Finding 4 - what the N in "Boom N" actually is, and where the measurement fails

The folk description is "a spike every N ticks". Taking the measured jump rate
and Deriv's ~1 tick/second, the implied seconds-between-spikes is:

| N | jumps/day | implied ticks/spike at 1 tick/s |
|---:|---:|---:|
| 1000 | 82.9 | 1,042 |
| 900 | 91.9 | 940 |
| 600 | 132.8 | 650 |
| 500 | 158.2 | 546 |
| 300 | 245.8 | 351 |
| 200 | 332.5 | 260 |
| 150 | 392.7 | 220 |
| 100 | 374.4 | 231 |
| 99 | 362.0 | 239 |
| 50 | 2.7 | 32,000 |

**For N ≥ 300 the description holds to within about 10%.** Below that it breaks
down, and Boom 50 fails by three orders of magnitude.

This is a **failure of the detector, not a property of the instrument**, and it
should not be read as "Boom 50 rarely spikes". The jump test flags moves beyond
5 robust sigmas of a 500-bar rolling MAD. When spikes are frequent and small
relative to background noise, they inflate the very MAD used to detect them and
fall below threshold. The small-N Boom indices have exactly that geometry. To
measure them properly the spikes must be counted on **tick data**, where they
are individual events rather than components of a one-minute bar. That pass has
not been run.

Where the detector does fire, roughly **half of all absolute price movement** in
a Boom index is carried by jumps (`jump_share_of_abs_move` 0.47-0.50 for N ≥ 99).

---

---
[All findings](../README.md)
