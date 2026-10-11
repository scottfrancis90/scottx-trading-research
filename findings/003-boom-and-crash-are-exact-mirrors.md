# Finding 3 - Boom and Crash are exact mirrors

Crash was included as a control, not as a subject. It did its job.

| N | Boom vol | Crash vol | Boom skew | Crash skew | Boom jumps/day | Crash jumps/day | Boom up-share | Crash up-share |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 4.004 | 3.992 | +1.317 | −1.299 | 2.7 | 2.5 | 1.000 | 0.000 |
| 99 | 5.060 | 5.060 | +1.856 | −1.862 | 362.0 | 361.4 | 1.000 | 0.000 |
| 100 | 4.941 | 5.053 | +1.903 | −1.888 | 374.4 | 369.2 | 1.000 | 0.000 |
| 150 | 5.619 | 5.592 | +2.329 | −2.297 | 392.7 | 393.3 | 0.983 | 0.017 |
| 200 | 6.012 | 6.011 | +2.701 | −2.666 | 332.5 | 334.8 | 0.957 | 0.041 |
| 300 | 101.359 | 102.379 | +3.267 | −3.324 | 245.8 | 246.0 | 0.957 | 0.039 |
| 500 | 30.193 | 30.420 | +4.226 | −4.243 | 158.2 | 156.8 | 0.968 | 0.032 |
| 600 | 27.878 | 27.936 | +4.647 | −4.697 | 132.8 | 132.9 | 0.973 | 0.028 |
| 900 | 22.827 | 22.832 | +5.771 | −5.732 | 91.9 | 91.2 | 0.979 | 0.017 |
| 1000 | 21.587 | 21.761 | +6.000 | −6.038 | 82.9 | 82.7 | 0.984 | 0.018 |

Volatility correlation across the ten pairs **1.00000**; jump-rate correlation
**0.99991**; the ten skew pairs sum to a mean of **−0.0029**, i.e. antisymmetry
to three decimal places.

So the measurement is trustworthy on these instruments, and Boom/Crash are one
generator with a sign flip. **Anything discovered on Boom must appear inverted
on Crash or it is an artifact.**

Note also that the number in the name is **not** volatility here: Boom 300
carries 101% annualised while Boom 500 carries 30%. Boom 300/Crash 300 are the
volatile outliers of the family by a factor of four.

---

---
[All findings](../README.md)
