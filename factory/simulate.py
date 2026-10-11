# Author: Scott (ScottX Research)
"""The one simulation engine. GA, controls, validation and the holdout all
use this and nothing else.

WHAT THIS FILE IS DEFENDING AGAINST
  Six harness bugs came out of the previous two days of work, and every one
  was the same shape: an ambiguity inside a single bar, resolved in the rule's
  favour. The worst of them (Finding 73) turned -0.025 R into +0.270 R and
  survived two out-of-sample checks, because an out-of-sample test confirms
  whatever the harness computes, including its errors.

  So the rules here are absolute and they are not configurable:

  1. A SIGNAL IS COMPLETE AT A BAR'S CLOSE. Acting on it starts at the next
     bar. Nothing reads a bar that has not closed.
  2. SAME BAR HITS BOTH STOP AND TARGET -> STOP. Always. There is no flag.
  3. ON THE BAR A PENDING ORDER FILLS, the target may NOT be counted. That
     bar's range contains movement from before the fill. The stop IS counted,
     which is the conservative side of the same ambiguity.
  4. FILLS ARE GAP-HONEST. A stop fills at the level or worse (exit_fill); a
     target or limit fills at the level or better (entry_fill). Gaps are paid.
  5. COSTS ALWAYS. Spread on entry plus SLIP_R, on every trade, no exceptions.
  7. OVERLAPPING PENDING ORDERS FILL IN TIME ORDER, never in signal
     order. Whichever level price reaches first is the one that fills,
     because that is the only one a live account gets.
  6. ONE POSITION AT A TIME unless a caller explicitly says otherwise.

  Rule 3 is the one that cost a day. It is written first in the walk so that
  it cannot be forgotten.
"""
import numpy as np
import pandas as pd

from factory.config import SLIP_R

# ---------------------------------------------------------------------------
# FILLS, named for what they are.
#
# An earlier helper pair, entry_fill/exit_fill, BOTH meant "at the level or
# WORSE" -- one for a stop-order entry, one for a protective stop. Neither is
# a limit fill. Used by name on the wrong two entry modes, every stop-order
# entry filled BETTER than its level and a near-zero breakout rule came out at
# about +0.9 R a trade. The regression gate caught it on its first run.
#
# So they are spelled out here. Four cases, each named for the order it is:
#   a STOP ORDER to enter   -> price ran through you   -> worse
#   a LIMIT ORDER to enter  -> price came to you       -> better
#   a PROTECTIVE STOP       -> price ran through you   -> worse
#   a TARGET (a limit exit) -> price came to you       -> better
# ---------------------------------------------------------------------------

def fill_stop_entry(level, bar_open, side):
    """buy stop above the market: a gap above fills at the open, not the level"""
    return max(level, bar_open) if side > 0 else min(level, bar_open)


def fill_limit_entry(level, bar_open, side):
    """buy limit below the market: a gap below fills at the open, which is better"""
    return min(level, bar_open) if side > 0 else max(level, bar_open)


def fill_protective(level, bar_open, side):
    """a long's stop is below: a gap down fills worse than the stop"""
    return min(level, bar_open) if side > 0 else max(level, bar_open)


def fill_target(level, bar_open, side):
    """a long's target is above: a gap above fills at the open, which is better"""
    return max(level, bar_open) if side > 0 else min(level, bar_open)

MARKET, STOP_ORDER, LIMIT_ORDER = "market", "stop", "limit"
AT_PRICE = "at_price"        # enter at a stated bar and a stated price

# WHY AT_PRICE EXISTS
#   A control has to be the SAME TRADES with one thing changed. Flipping the
#   side of a limit order does not do that: the order lands on the wrong side
#   of the market and most of the trades stop existing. Measured on a real
#   genome -- rule 250 trades, inverted control 68, shuffled 170 of which 141
#   were still the rule's own direction. The controls were scoring a smaller,
#   self-selected sample and the gate built on them meant nothing.
#   AT_PRICE takes the rule's actual fills and re-runs them, so n is identical
#   and only the direction differs.


def walk(o, h, l, c, sp, signals, timeout, order_life=0, one_at_a_time=True, end_cap=None,
         min_r_spreads=0.0, partial_at=None, trail_atr=None, atr_arr=None):
    """turn signals into trades.

    signals: iterable of dicts, each with
        bar       the bar whose CLOSE produced the signal
        side      +1 long, -1 short
        mode      MARKET | STOP_ORDER | LIMIT_ORDER
        entry     price for a pending order; ignored for MARKET
        stop      price
        target    price
    order_life: bars a pending order may rest. 0 means it must fill on the
                very next bar or it is cancelled.

    Returns a DataFrame with one row per trade actually taken.
    """
    n = len(c) if end_cap is None else min(int(end_cap), len(c))
    out = []
    busy_until = -1

    # RULE 7 (added 2026-09-27, defect 12). PENDING ORDERS FILL IN TIME ORDER.
    #
    # A one-sided pending trigger emits on every eligible bar, so dozens of
    # resting orders overlap. This loop used to walk the signals in BAR order
    # and take the first one that filled -- which means it could take an order
    # signalled earlier but TOUCHED LATER, passing over an order that price
    # actually reached first. A live account has no such choice: whichever
    # level price reaches first is the one that fills.
    #
    # Measured on the Finding 81 candidate, signal order vs time order:
    #     TRAIN    +0.3185  ->  +0.0042
    #     VALIDATE +0.1149  ->  -0.1488
    # and the two books shared only 40% of their trades. The whole edge was in
    # the choice, not in the market. So resolve fills by fill bar, breaking
    # ties by the earlier signal.
    if one_at_a_time:
        pre = []
        for idx, s in enumerate(signals):
            if s["mode"] in (MARKET, AT_PRICE):
                pre.append((int(s["bar"]) + (1 if s["mode"] == MARKET else 0), idx))
                continue
            i0 = int(s["bar"])
            side0 = int(s["side"])
            lvl0 = float(s["entry"])
            last0 = min(i0 + 1 + max(order_life, 0), n - 2)
            for q in range(i0 + 1, last0 + 1):
                if s["mode"] == STOP_ORDER:
                    hit0 = (h[q] >= lvl0) if side0 > 0 else (l[q] <= lvl0)
                else:
                    hit0 = (l[q] <= lvl0) if side0 > 0 else (h[q] >= lvl0)
                if hit0:
                    pre.append((q, idx))
                    break
        pre.sort()
        signals = [signals[idx] for _, idx in pre]

    for s in signals:
        i = int(s["bar"])
        side = int(s["side"])
        if i + 1 >= n - 1:
            continue
        # An order may only be PLACED while flat, and may only fill after the
        # previous trade has closed. Checking the signal bar alone let an order
        # placed mid-trade fill the instant the position closed.
        if one_at_a_time and i <= busy_until:
            continue

        # ---- find the fill
        if s["mode"] == AT_PRICE:
            fill_bar = i
            fill_px = float(s["entry"]) + (sp if side > 0 else 0.0)
        elif s["mode"] == MARKET:
            fill_bar = i + 1
            fill_px = o[fill_bar] + (sp if side > 0 else 0.0)   # pay the ask to buy
        else:
            lvl = float(s["entry"])
            fill_bar = None
            last = min(i + 1 + max(order_life, 0), n - 2)
            for q in range(i + 1, last + 1):
                if s["mode"] == STOP_ORDER:
                    hit = (h[q] >= lvl) if side > 0 else (l[q] <= lvl)
                    if hit:
                        fill_px = fill_stop_entry(lvl, o[q], side) + (sp if side > 0 else 0.0)
                        fill_bar = q
                        break
                else:
                    hit = (l[q] <= lvl) if side > 0 else (h[q] >= lvl)
                    if hit:
                        fill_px = fill_limit_entry(lvl, o[q], side) + (sp if side > 0 else 0.0)
                        fill_bar = q
                        break
            if fill_bar is None:
                continue

        stop_px = float(s["stop"])
        tgt_px = float(s["target"])
        R = (fill_px - stop_px) if side > 0 else (stop_px - fill_px)
        if not np.isfinite(R) or R <= 0:
            continue
        # THE FLOOR IS ON THE REALISED R, not the intended one. A limit that
        # fills on a favourable gap lands closer to its stop than planned, and
        # the remaining R can collapse to a fraction of the spread. That is
        # what produced a +584 R trade on a 3.2-cent stop in the first real
        # GA run. No broker would accept the order; neither does this.
        if min_r_spreads > 0 and sp > 0 and R < min_r_spreads * sp:
            continue
        cost = sp / R + SLIP_R

        # ---- exits that MOVE. Both are genes, both are conservative:
        #   partial_at  take half off at that R, and move the stop to breakeven
        #               on the remainder. The half that is banked is banked --
        #               it cannot be given back by the rest of the trade.
        #   trail_atr   after the partial (or from entry if there is none),
        #               trail the stop by k x ATR behind the best price seen.
        #               The stop only ever moves in the trade's favour.
        # A trailing stop is checked on the bar AFTER it moves, never on the
        # same bar that set the new high -- otherwise the trail can be hit by
        # the very move that created it.
        banked = 0.0
        frac = 1.0
        best = fill_px

        # ---- walk it forward
        # RULE 3: on the fill bar the target does not count. On a MARKET entry
        # the fill bar IS the entry bar and we entered at its open, so the
        # whole bar is after us and the target may count from it. Only a
        # PENDING fill carries pre-fill movement.
        # AT_PRICE counts as PENDING. It re-enters a trade that originally
        # filled from a resting order, so it must inherit that order's
        # restriction: the target may not be booked on the entry bar. Without
        # this the control is slightly more generous than the rule it is
        # controlling, and the two disagree by up to 4 R on trades that are
        # supposed to be identical.
        pending = s["mode"] != MARKET
        end = min(fill_bar + timeout, n - 1)
        r, why = None, "time"
        for q in range(fill_bar, end + 1):
            hit_s = (l[q] <= stop_px) if side > 0 else (h[q] >= stop_px)
            allow_t = (not pending) or (q > fill_bar)
            hit_t = allow_t and ((h[q] >= tgt_px) if side > 0 else (l[q] <= tgt_px))
            if hit_s:                                  # RULE 2: stop wins ties
                px = fill_protective(stop_px, o[q], side)
                r = banked + frac * (side * (px - fill_px) / R) - cost
                why = "stop" if frac == 1.0 else "stop after partial"
                break
            if hit_t:
                px = fill_target(tgt_px, o[q], side)
                r = banked + frac * (side * (px - fill_px) / R) - cost
                why = "target"
                break
            # --- the partial, taken at its level, once
            if partial_at and frac == 1.0 and allow_t:
                lvl = fill_px + side * partial_at * R
                reached = (h[q] >= lvl) if side > 0 else (l[q] <= lvl)
                if reached:
                    banked = 0.5 * partial_at
                    frac = 0.5
                    stop_px = fill_px          # breakeven on the remainder
            # --- the trail, only from the bar after the extreme that set it
            if trail_atr and atr_arr is not None and q > fill_bar:
                a = atr_arr[q]
                if np.isfinite(a) and a > 0:
                    best = max(best, h[q]) if side > 0 else min(best, l[q])
                    cand = best - side * trail_atr * a
                    if (side > 0 and cand > stop_px) or (side < 0 and cand < stop_px):
                        stop_px = cand
        if r is None:
            r = banked + frac * (side * (c[end] - fill_px) / R) - cost
            end_bar = end
        else:
            end_bar = q
        out.append(dict(sig_bar=i, fill_bar=fill_bar, exit_bar=end_bar, side=side,
                        entry=fill_px, stop=stop_px, stop0=fill_px - side * R, target=tgt_px,
                        R=r, why=why, rr=abs(tgt_px - fill_px) / R,
                        r_spreads=(R / sp) if sp > 0 else np.nan))
        busy_until = end_bar
    return pd.DataFrame(out)


def metrics(R):
    R = np.asarray(R, float)
    if len(R) < 30:
        return None
    eq = np.cumsum(R)
    dd = float((np.maximum.accumulate(eq) - eq).max())
    k = len(R) // 2
    se = R.std(ddof=1) / np.sqrt(len(R))
    kk = max(1, len(R) // 100)
    return dict(n=len(R), mean=float(R.mean()), t=float(R.mean() / se) if se else np.nan,
                win=float((R > 0).mean()), total=float(eq[-1]), dd=dd,
                rdd=float(eq[-1] / dd) if dd > 0 else np.nan,
                trim=float(np.sort(R)[kk:-kk].mean()),
                m1=float(R[:k].mean()), m2=float(R[k:].mean()))


def show(lab, d, width=46):
    m = metrics(d["R"] if isinstance(d, pd.DataFrame) else d)
    if m is None:
        n = 0 if d is None else len(d)
        print("%-*s n=%5d  (too few)" % (width, lab, n))
        return None
    print("%-*s n=%5d mean %+7.4f trim %+7.4f t %6.2f win %5.1f%% total %+8.1f R/DD %6.2f halves %+7.4f/%+7.4f" % (
        width, lab, m["n"], m["mean"], m["trim"], m["t"], 100 * m["win"], m["total"],
        m["rdd"], m["m1"], m["m2"]))
    return m


def random_control(o, h, l, c, sp, n_signals, stop_atr, target_r, timeout, atr, seed=0):
    """the control that decides whether the ENGINE is honest.

    Same machinery, same stop distance distribution, same target multiple,
    random bars and random sides. It must come back at roughly minus the
    trading cost. If it does not, the engine is wrong and nothing measured
    with it means anything -- whatever the rule scores.
    """
    rng = np.random.default_rng(seed)
    n = len(c)
    sigs = []
    for _ in range(int(n_signals)):
        b = int(rng.integers(50, n - timeout - 3))
        a = atr[b]
        if not np.isfinite(a) or a <= 0:
            continue
        side = 1 if rng.random() < 0.5 else -1
        ref = c[b]
        R = stop_atr * a
        sigs.append(dict(bar=b, side=side, mode=MARKET, entry=np.nan,
                         stop=ref - side * R, target=ref + side * target_r * R))
    return walk(o, h, l, c, sp, sigs, timeout, one_at_a_time=False)


def atr(h, l, c, n=14):
    tr = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    return np.concatenate([[np.nan], pd.Series(tr).rolling(n).mean().to_numpy()])
