# Author: Scott (ScottX Research)
"""Genome -> signals -> trades. The only place a genome touches the market.

Signals are complete at a bar's CLOSE and acted on from the next bar. Every
indicator is computed on the whole series with backward-looking windows, so a
bar's value never depends on which split it is evaluated in, and never on a
bar that has not closed yet.

A two-sided trigger (both rails) emits an order on each rail. The engine
fills pending orders in TIME order and holds one position at a time, so
whichever rail price reaches first is the trade -- exactly what a live
account gets. Emitting both and taking them in list order would silently
give the long side priority.
"""
import numpy as np
import pandas as pd

from factory.config import BARS_PER_DAY, MIN_R_SPREADS
from factory.simulate import LIMIT_ORDER, MARKET, STOP_ORDER, atr, walk

ORDER_LIFE = 0        # a pending order is re-placed every bar at the current rail
WARMUP = 250          # bars before any signal, so every indicator is defined


def timeout_bars(g):
    """the hold limit in BARS, from a gene stored in HOURS"""
    return max(5, int(round(g["timeout"] * BARS_PER_DAY[g["tf"]] / 24.0)))


def _ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()


def rails(g, h, l, c, A):
    """(upper, lower) levels for the genome's context, known at each bar's close"""
    d = g["context"]
    if d["gene"] == "prior_range":
        n = d["lookback"]
        up = pd.Series(h).rolling(n).max().shift(1).to_numpy()     # previous n bars, not this one
        dn = pd.Series(l).rolling(n).min().shift(1).to_numpy()
    else:
        mid = _ema(c, 20)
        up, dn = mid + d["k"] * A, mid - d["k"] * A
    return up, dn


def side_ok(g, i, side, c, ema_f, A, A_med):
    f = g["filter"]
    if f["gene"] == "trend_ema":
        return (c[i] > ema_f[i]) if side > 0 else (c[i] < ema_f[i])
    if f["gene"] == "atr_band":
        r = A[i] / A_med[i] if A_med[i] > 0 else np.nan
        return bool(np.isfinite(r) and f["lo"] <= r <= f["hi"])
    return True


def build_signals(g, o, h, l, c, i0, i1):
    A = atr(h, l, c)
    up, dn = rails(g, h, l, c, A)
    f = g["filter"]
    ema_f = _ema(c, f["period"]) if f["gene"] == "trend_ema" else None
    A_med = pd.Series(A).rolling(500, min_periods=100).median().shift(1).to_numpy() if f["gene"] == "atr_band" else None
    tr, st, tg = g["trigger"], g["stop"], g["target"]
    ema_t = _ema(c, tr["period"]) if tr["gene"] == "ema_cross" else None
    want = tr.get("side", "both")
    sides = [s for s in (1, -1) if want == "both" or (want == "long") == (s > 0)]

    def stop_target(side, entry, i):
        stop = (dn[i] if side > 0 else up[i]) if st["gene"] == "other_side" else entry - side * st["k"] * A[i]
        R = side * (entry - stop)
        if not np.isfinite(R) or R <= 0:
            return None
        if tg["gene"] == "opposite_level":          # a fade targets the other rail
            target = up[i] if side > 0 else dn[i]
        else:
            target = entry + side * tg["r"] * R
        if side * (target - entry) <= 0:
            return None
        return stop, target

    sigs = []
    for i in range(max(i0, WARMUP), i1 - 1):
        if not (np.isfinite(A[i]) and np.isfinite(up[i]) and np.isfinite(dn[i])):
            continue
        if tr["gene"] == "ema_cross":
            cross = 1 if (c[i - 1] <= ema_t[i - 1] and c[i] > ema_t[i]) else (
                -1 if (c[i - 1] >= ema_t[i - 1] and c[i] < ema_t[i]) else 0)
            if cross == 0 or not side_ok(g, i, cross, c, ema_f, A, A_med):
                continue
            stp = stop_target(cross, c[i], i)
            if stp:
                sigs.append(dict(bar=i, side=cross, mode=MARKET, entry=np.nan, stop=stp[0], target=stp[1]))
            continue
        for side in sides:
            if not side_ok(g, i, side, c, ema_f, A, A_med):
                continue
            if tr["gene"] == "break_level":        # stop order beyond the rail, price not there yet
                lvl, mode = (up[i], STOP_ORDER) if side > 0 else (dn[i], STOP_ORDER)
                if (c[i] >= lvl) if side > 0 else (c[i] <= lvl):
                    continue
            else:                                  # fade: buy limit at the lower rail, sell limit at the upper
                lvl, mode = (dn[i], LIMIT_ORDER) if side > 0 else (up[i], LIMIT_ORDER)
                if (c[i] <= lvl) if side > 0 else (c[i] >= lvl):
                    continue
            stp = stop_target(side, lvl, i)
            if stp:
                sigs.append(dict(bar=i, side=side, mode=mode, entry=lvl, stop=stp[0], target=stp[1]))
    return sigs


def run(g, which, sp=None, sym=None):
    """the genome's trades on one split.

    Indicators are computed on the full series; signals are only emitted
    inside the split; and a trade may not run past the split's last bar --
    the embargo between splits is longer than the longest trade.
    """
    from factory import data
    tf = g["tf"]
    df = data.load(tf, sym)
    i0, i1 = data.index_range(tf, which, sym)
    if i1 - i0 < 200:
        return None
    if sp is None:
        sp = data.spread_price(tf, "train", sym)
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    sigs = build_signals(g, o, h, l, c, i0, i1)
    if len(sigs) < 5:
        return None
    trail = g["manage"].get("k") if g["manage"]["gene"] == "trail" else None
    return walk(o, h, l, c, sp, sigs, timeout_bars(g), order_life=ORDER_LIFE, end_cap=i1,
                min_r_spreads=MIN_R_SPREADS, trail_atr=trail, atr_arr=atr(h, l, c) if trail else None)
