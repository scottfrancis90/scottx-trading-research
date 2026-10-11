# Author: Scott (ScottX Research)
"""Which symbols the factory searches, and how independent they really are.

With one symbol the only defences are the time splits, the controls and the
ledger. With several, a real edge should show up on MOST of them while noise
shows up on one or two -- so a genome is scored on POOLED trades and gated on
how many symbols it works on.

Correlated symbols are not independent tests. Six pairs that share a currency
can all turn positive on one currency move. So the gate counts EFFECTIVE
independent symbols, from the eigenvalue spectrum of their return correlations.

Selected by environment, not by a runtime global, because worker processes
re-import every module in a fresh interpreter and would not see a global.
    FACTORY_SYMBOLS=SYNTH1,SYNTH2,SYNTH3
"""
import os

SYMBOLS = tuple(s.strip() for s in os.environ.get("FACTORY_SYMBOLS", "SYNTH1").split(",") if s.strip())


def timeframes(default):
    return default


def symbols():
    return SYMBOLS


def is_fx():
    """True when several symbols are searched together (cross-section on)."""
    return len(SYMBOLS) > 1


_CORR = {}


def corr_matrix():
    """daily-return correlations across the symbols, TRAIN era only."""
    import numpy as np
    import pandas as pd
    from factory import data
    from factory.config import TIMEFRAMES
    if _CORR:
        return _CORR["C"], _CORR["names"]
    base = TIMEFRAMES[0]
    ser = {}
    for sym in SYMBOLS:
        d = data.load(base, sym)
        i0, i1 = data.index_range(base, "train", sym)
        g = d.iloc[i0:i1].set_index("time")["close"].resample("1D").last().dropna()
        ser[sym] = np.log(g).diff()
    X = pd.DataFrame(ser).dropna()
    _CORR["C"] = X.corr()
    _CORR["names"] = list(X.columns)
    return _CORR["C"], _CORR["names"]


def effective_independent(syms):
    """how many INDEPENDENT bets a set of symbols really represents.

    Entropy of the eigenvalue spectrum: exp(-sum p log p) over the normalised
    eigenvalues of the correlation sub-matrix. Identical symbols collapse to 1,
    unrelated symbols count in full.
    """
    import numpy as np
    syms = [s for s in syms if s in SYMBOLS]
    if len(syms) <= 1:
        return float(len(syms))
    C, _ = corr_matrix()
    M = C.loc[syms, syms].to_numpy()
    ev = np.linalg.eigvalsh(M)
    ev = ev[ev > 1e-9]
    if not len(ev):
        return 1.0
    p = ev / ev.sum()
    return float(np.exp(-(p * np.log(p)).sum()))
