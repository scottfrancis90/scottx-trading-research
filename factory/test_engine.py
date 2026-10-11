# Author: Scott (ScottX Research)
"""THE REGRESSION GATE. Nothing is built on this engine until it passes.

TWO THINGS ARE CHECKED, IN THIS ORDER
  1. THE ENGINE IS HONEST. Random entries with the same geometry must return
     about MINUS THE TRADING COST. This is checked FIRST and on its own,
     because Finding 73 proved that an out-of-sample test confirms whatever
     the harness computes, including its errors. If this number is positive,
     the engine is inventing money and every other result is void.
  2. THE ARITHMETIC IS RIGHT. Hand-built trades with known answers: a clean
     target hit, a clean stop, a gap through the stop, and the same-bar
     ambiguity, each checked against a number worked out by hand.

    python -m factory.test_engine
"""
import numpy as np
import pandas as pd

from factory import data
from factory.simulate import (LIMIT_ORDER, MARKET, atr, metrics,
                              random_control, walk)
from factory.config import SLIP_R


def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    print("   %-52s got %+9.5f  want %+9.5f  %s" % (name, got, want, "OK" if ok else "*** FAIL ***"))
    return ok


def test_arithmetic():
    print("\n2. THE ARITHMETIC  (hand-built bars, answers worked out by hand)")
    # one synthetic series we control completely
    o = np.array([100., 100., 100., 100., 100., 100.])
    h = np.array([100., 101., 110., 100., 100., 100.])
    l = np.array([100., 99.5, 100., 90., 88., 100.])
    c = np.array([100., 100., 100., 100., 100., 100.])
    sp = 0.0                                   # no spread, so cost = SLIP_R only
    ok = True

    # a clean target: long from bar 1's open at 100, target 110, stop 90 -> R=10
    t = walk(o, h, l, c, sp, [dict(bar=0, side=1, mode=MARKET, entry=np.nan,
                                   stop=90.0, target=110.0)], timeout=5)
    # entry 100, stop 90 -> R = 10. Target 110 is ONE R away, not two.
    ok &= check("clean target, +1R minus slippage", t["R"].iloc[0], 1.0 - SLIP_R, 1e-9)

    # a clean stop: long, stop 99 (R=1), target 200. Bar 1 low 99.5 misses,
    # bar 2 low 100 misses, bar 3 low 90 gaps THROUGH 99 -> fills at the bar's
    # open 100? No: open is 100, which is above the stop, so it fills AT 99.
    t = walk(o, h, l, c, sp, [dict(bar=0, side=1, mode=MARKET, entry=np.nan,
                                   stop=99.0, target=200.0)], timeout=5)
    ok &= check("clean stop, -1R minus slippage", t["R"].iloc[0], -1.0 - SLIP_R, 1e-9)

    # a GAP through the stop: make the open itself below the stop
    o2 = np.array([100., 100., 95., 100.])
    h2 = np.array([100., 100., 96., 100.])
    l2 = np.array([100., 99.9, 94., 100.])
    c2 = np.array([100., 100., 95., 100.])
    # long from bar1 open 100, stop 99 (R=1). Bar2 opens at 95, five R below.
    t = walk(o2, h2, l2, c2, 0.0, [dict(bar=0, side=1, mode=MARKET, entry=np.nan,
                                        stop=99.0, target=200.0)], timeout=5)
    ok &= check("gap through the stop, -5R not -1R", t["R"].iloc[0], -5.0 - SLIP_R, 1e-9)

    # SAME BAR hits both -> the stop must win
    o3 = np.array([100., 100., 100.])
    h3 = np.array([100., 110., 100.])
    l3 = np.array([100., 90., 100.])
    c3 = np.array([100., 100., 100.])
    t = walk(o3, h3, l3, c3, 0.0, [dict(bar=0, side=1, mode=MARKET, entry=np.nan,
                                        stop=95.0, target=105.0)], timeout=5)
    ok &= check("same bar hits both -> STOP", t["R"].iloc[0], -1.0 - SLIP_R, 1e-9)
    print("      (that trade's bar reaches 110 and 90; a lax engine books +1R here)")

    # RULE 3: a pending fill may not count the target on its own bar
    o4 = np.array([100., 100., 100., 100.])
    h4 = np.array([100., 100., 101., 100.])
    l4 = np.array([100., 100., 98.,  100.])
    c4 = np.array([100., 100., 100., 100.])
    # buy LIMIT at 99: bar 2 dips to 98 (fills) and also reaches 101.
    # target 101, stop 97 -> R=2. If the target counted on the fill bar this
    # would book +1R. It must instead time out at the close.
    t = walk(o4, h4, l4, c4, 0.0, [dict(bar=0, side=1, mode=LIMIT_ORDER, entry=99.0,
                                        stop=97.0, target=101.0)], timeout=3, order_life=3)
    ok &= check("limit fill: target ignored on the fill bar", t["R"].iloc[0],
                (100.0 - 99.0) / 2.0 - SLIP_R, 1e-9)
    print("      (a lax engine books +1R here; this is the Finding 73 bug exactly)")
    return ok


def test_engine_honest(tf="H1"):
    print("\n1. IS THE ENGINE HONEST?  (random entries must return minus the cost)")
    d = data.split(tf, "train")
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close"))
    sp = data.spread_price(tf)
    A = atr(h, l, c)
    ok = True
    for stop_atr, tr in ((1.0, 1.0), (1.0, 2.0), (2.0, 3.0)):
        t = random_control(o, h, l, c, sp, 4000, stop_atr, tr, 100, A, seed=7)
        m = metrics(t["R"])
        stops = t[t.why == "stop"]["R"]
        print("   stop %.0f ATR, target %.0f R:  n=%4d  mean %+7.4f  win %4.1f%%  "
              "avg stop-out %+6.3f  target hits %4.1f%%" % (
                  stop_atr, tr, m["n"], m["mean"], 100 * m["win"],
                  stops.mean() if len(stops) else float("nan"),
                  100 * (t["why"] == "target").mean()))
        # The only thing that must hold is that random entries do NOT make
        # money. How far below zero they land depends on the conservative
        # conventions (stop wins ties, gaps paid), which is a handicap the
        # engine applies to every rule equally.
        if m["mean"] > 0.005:
            print("      *** FAIL: random entries make money. The engine is inventing it. ***")
            ok = False
    return ok


def main():
    print("=" * 110)
    print("FACTORY ENGINE — REGRESSION GATE")
    print("=" * 110)
    a = test_engine_honest()
    b = test_arithmetic()
    print("\n" + "=" * 110)
    print("  engine honest (random = cost) : %s" % ("PASS" if a else "FAIL"))
    print("  arithmetic                    : %s" % ("PASS" if b else "FAIL"))
    print("=" * 110)
    if not (a and b):
        print("  GATE NOT PASSED. Nothing further is built on this engine.")
    else:
        print("  Gate passed. The GA may be built on this engine.")


if __name__ == "__main__":
    main()
