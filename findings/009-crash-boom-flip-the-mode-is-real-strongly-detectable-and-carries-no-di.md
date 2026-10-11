# Finding 9 - Crash Boom Flip: the mode is real, strongly detectable, and carries no direction

The first genuinely new structure in this study, followed all the way to its
economic conclusion. Data: M1, 2026-07-17 to 2026-08-30, 63,784 bars.

### 9a - the mode exists, and it is not marginal

Jump signs at M1, k = 5 robust sigma. Under independence
P(same sign) = p^2 + (1-p)^2.

| symbol | jumps | up share | P(same) | chance | excess | z |
|---|---:|---:|---:|---:|---:|---:|
| Flip 1000 | 14,291 | 0.590 | **0.869** | 0.516 | +0.353 | **84.3** |
| Flip 500 | 10,255 | 0.553 | **0.765** | 0.506 | +0.259 | **52.4** |
| Flip 300 | 3,264 | 0.440 | **0.629** | 0.507 | +0.122 | **13.9** |
| Flip 150 | 347 | 0.467 | **0.590** | 0.502 | +0.087 | **3.3** |
| *Boom 99 (control)* | 25,013 | 1.000 | 1.000 | 1.000 | 0.000 | 0.0 |
| *Boom 100 (control)* | 25,872 | 1.000 | 1.000 | 1.000 | −0.000 | −0.0 |

All four positive, monotone in N, and the controls behave exactly as they
must. And the between-spike drift **reverses with the mode** - Flip 1000
drifts −0.443 bp/bar in up-spike mode and +0.430 bp/bar in down-spike mode.
That is the Boom/Crash structure with a switch on top.

### 9b - two errors made and caught before reporting

A first economic pass produced a "drift inside one mode divided by one
spread" ratio of **445x**. It was wrong twice over, and both errors are the
kind that manufacture an edge:

* **The spike bars were masked out** before measuring the drift. Boom and
  Crash are martingales precisely because drift and spike cancel. Deleting
  the spikes deletes the half that pays for the other half.
* **Each run was measured from its first to its LAST same-sign spike**, which
  requires knowing when the run ended - the same hindsight that invalidated
  the gold project's P10 daily-selection rule.

### 9c - the causal test, and the overlap trap

Detector shifted one bar so a return cannot influence its own threshold.
Enter at the close of the spike bar, short after an up-spike, hold h bars,
count every subsequent bar including later spikes, charge one spread.

Run naively this looked significant - **7 of 28 cells at |t| > 2** where
chance expects 1.4, with Flip 1000 at h=120 reading t = −11.3. But at h = 120
there were 14,187 positions drawn from 63,784 bars, so each overlaps about
120 others. Overlap inflates t by roughly sqrt(h) ~ 11.

Restricting to **non-overlapping** positions:

| | h=1 | h=2 | h=5 | h=10 | h=30 | h=60 | h=120 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Flip 1000 | +0.14 | −0.39 | −0.79 | −0.36 | −0.55 | −0.11 | −0.94 |
| Flip 500 | +0.06 | −0.34 | −1.25 | +1.29 | +1.69 | +0.06 | +0.92 |
| Flip 300 | −0.91 | +0.17 | −1.10 | −0.02 | −1.46 | −0.19 | −1.09 |
| Flip 150 | −1.58 | −0.09 | −0.53 | −1.58 | +0.40 | −0.56 | −0.87 |

**0 of 28 cells exceed |t| = 2, where chance expects 1.4. Maximum |t| is
1.69.** Sign agreement across the four instruments is a coin flip at every
horizon (0-2 of 4 positive). Every one of the seven apparently significant
results was an artifact of overlapping windows.

### 9d - what this means

**The mode is real and the mode is useless for direction.** Both statements
hold simultaneously, and the reason is structural rather than empirical: Boom
is a martingale and Crash is a martingale, so an instrument that alternates
between them is a martingale *in both modes*. Perfect mode detection tells
you which side the **skew** is on, never which way the price is going. The
z = 84 detection and the t < 2 payoff are not in tension; the first was never
going to produce the second.

What the mode is genuinely good for is knowing **which side can gap through a
stop**. In up-spike mode a short position can be jumped against; a long
cannot. That is a real risk-management fact with a real measurement behind
it, and it is the only actionable thing this study has produced about any
synthetic instrument.

---

---
[All findings](../README.md)
