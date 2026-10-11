# Finding 90 - correction to Finding 89: the retrace IS the entry. Re-measured, the trades get fair odds and nothing more.

*2026-09-27. FX, 17 pairs, daily and H4, TRAIN + VALIDATE. Holdout not read.*

### My error

Finding 89 measured: level A breaks, does price reach the next pool B **before
returning to A**? A return to A was scored as a FAILURE.

The user: *"you said once one brake you enter that is wrong... when a break
occur you see where i go and wait for price to come and i enter"*.

**The return to A is not the failure. It is the ENTRY.** Price breaks the
level, comes back to it, and the trade is taken there. Finding 89 measured a
rule nobody trades and reported it as the user's.

### The sequence actually measured now

1. a CLOSE through a live wick-marked level A -- the break
2. B = nearest live level ahead -- the destination
3. price RETURNS to touch A within the wait window -- **the entry**
4. stop = the extreme of the bar that returned, i.e. beyond the wick
5. does price reach B before that stop?

Null, per event, measured from the entry:
`P(reach B first) = dist_stop / (dist_stop + dist_B)`.

### Result

| | TRAIN | VALIDATE |
|---|---|---|
| Daily | -1.20 pp (n=2,022, t -1.44) | -0.82 pp (n=1,017, t -0.67) |
| H4 | -0.64 pp (n=11,377, t -1.76) | **-1.20 pp** (n=5,944, t -2.42) |

Hit rate 14.8-16.0% against a geometric 16.0-16.7%. All four cells negative;
H4 validation significantly so on nearly six thousand events.

### What IS real, and it is worth keeping

**Median reward-to-risk is 7.6 : 1.** Waiting for the retrace puts the entry
right next to its invalidation with the target far away -- exactly what the
user means by *"good entry give you good SL"*. The trade GEOMETRY this method
produces is better than anything the factory generated in 8,649 genomes.

The selection is what fails. At 7.6:1 geometry requires roughly 16% and the
method delivers 15-16%. **Fair odds, not favourable ones** -- and fair odds
minus the spread is a slow loss.

That is a different failure from the rest of today: the chapter method died
because its stops sat inside the spread, the GA died on artifacts. This one has
excellent geometry and lands exactly on the line chance predicts.

**Finding 89's daily positive is superseded. It measured the wrong sequence.**

---

---
[All findings](../README.md)
