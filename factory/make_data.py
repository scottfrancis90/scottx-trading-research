# Author: Scott (ScottX Research)
"""Synthetic bars, so the factory can be run without any broker data.

    python -m factory.make_data [n_symbols] [years] [--edge]

Writes data/SYNTH<k>_H1.csv and data/SYNTH<k>_H4.csv (24/5 hourly bars, a
random walk with volatility that changes over time, and a spread column).

Without --edge the market is pure noise. That is the most useful test there
is: the factory MUST report zero survivors on it. If it ever "finds" an edge
in a random walk, something in the pipeline is leaking.

With --edge a small, real effect is planted -- after a 40-bar breakout the
next bars drift slightly in the breakout direction -- so you can watch the
gates let a genuine effect through and see how strong it has to be.
"""
import os
import sys

import numpy as np
import pandas as pd


def make(sym, years=10, seed=0, edge=False, out="data"):
    rng = np.random.default_rng(seed)
    t = pd.date_range("2015-01-05", periods=int(years * 365 * 24), freq="h")
    t = t[t.dayofweek < 5]                                   # 24/5 like FX
    n = len(t)
    vol = 0.0015 * np.exp(np.cumsum(rng.normal(0, 0.02, n)) * 0.1)   # slowly drifting volatility
    vol = np.clip(vol, 0.0005, 0.005)
    r = rng.normal(0, 1, n) * vol
    if edge:                                                 # planted momentum after a breakout
        px = 100 * np.exp(np.cumsum(r))
        hi = pd.Series(px).rolling(40).max().shift(1).to_numpy()
        lo = pd.Series(px).rolling(40).min().shift(1).to_numpy()
        push = np.zeros(n)
        for i in range(41, n - 10):
            if px[i] > hi[i]:
                push[i + 1:i + 11] += 0.08 * vol[i]
            elif px[i] < lo[i]:
                push[i + 1:i + 11] -= 0.08 * vol[i]
        r = r + push
    close = 100 * np.exp(np.cumsum(r))
    open_ = np.r_[close[0], close[:-1]]
    wig = np.abs(rng.normal(0, 1, (2, n))) * vol * close * 0.6
    high = np.maximum(open_, close) + wig[0]
    low = np.minimum(open_, close) - wig[1]
    spread = np.round(close * 0.00012, 6)                    # ~1.2 bps
    d = pd.DataFrame(dict(time=t, open=open_, high=high, low=low, close=close, spread=spread))
    os.makedirs(out, exist_ok=True)
    d.to_csv(os.path.join(out, "%s_H1.csv" % sym), index=False)
    h4 = d.set_index("time").resample("4h").agg(dict(open="first", high="max", low="min",
                                                     close="last", spread="median")).dropna().reset_index()
    h4.to_csv(os.path.join(out, "%s_H4.csv" % sym), index=False)
    return len(d), len(h4)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    k = int(args[0]) if args else 1
    years = float(args[1]) if len(args) > 1 else 10
    edge = "--edge" in sys.argv
    out = os.environ.get("FACTORY_DATA", "data")
    for j in range(1, k + 1):
        n1, n4 = make("SYNTH%d" % j, years, seed=j, edge=edge, out=out)
        print("SYNTH%d: %d H1 bars, %d H4 bars -> %s%s" % (j, n1, n4, out, "  (edge planted)" if edge else ""))
