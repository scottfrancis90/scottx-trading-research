"""Forex pairs that move OPPOSITE each other.
  data    one CSV of daily bars per pair (columns: time, close), file name = symbol,
          e.g. data/EURUSD.csv. Daily log returns, aligned on common dates.
  step 1  EXHAUSTIVE pairwise correlation (every pair checked -- small space),
          in 3 periods (2017-20, 2021-23, 2024-26) + share of rolling 60-day
          windows that are negative, so a one-period accident is visible.
  step 2  GA for GROUPS: choose group A and group B (1-3 pairs each, equal weight)
          to make A's average return move most opposite B's (most negative
          correlation), on 2017-2021, then checked on 2022-2026 (unseen by the GA).
usage:  python fx_opposite.py path/to/daily_csv_folder
"""
import glob, os, itertools, sys
import numpy as np, pandas as pd

S = sys.argv[1] if len(sys.argv) > 1 else "data"
closes = {}
for f in glob.glob(S + "/*.csv"):
    sym = os.path.basename(f)[:-4]
    d = pd.read_csv(f, parse_dates=["time"]); d["time"] = d["time"].dt.normalize()
    d = d[d.time.dt.dayofweek < 5].drop_duplicates("time").set_index("time")["close"]
    closes[sym] = d
P = pd.DataFrame(closes).sort_index()
R = np.log(P).diff()
R = R[R.abs().max(axis=1) < 0.15]                 # drop bad prints
syms = sorted(R.columns)
periods = {"2017-20": ("2017", "2020"), "2021-23": ("2021", "2023"), "2024-26": ("2024", "2026")}
print("pairs:", len(syms), " ".join(syms))

rows = []
for a, b in itertools.combinations(syms, 2):
    x = R[[a, b]].dropna()
    rec = dict(a=a, b=b)
    for k, (s, e) in periods.items():
        y = x.loc[s:e]
        rec[k] = y[a].corr(y[b]) if len(y) > 200 else np.nan
    y = x.loc["2017":]
    roll = y[a].rolling(60).corr(y[b]).dropna()
    rec["neg_share"] = (roll < 0).mean() if len(roll) else np.nan
    rows.append(rec)
T = pd.DataFrame(rows)
T["worst"] = T[list(periods)].max(axis=1)          # least negative period = how reliable
neg = T[T["2024-26"] < -0.3].sort_values("2024-26")
print("\nMOST OPPOSITE PAIRS (daily returns correlation; -1 = perfect mirror)")
print("  %-7s %-7s %8s %8s %8s %12s" % ("pair A", "pair B", "2017-20", "2021-23", "2024-26", "neg 60d win"))
for r in neg.itertuples():
    f = lambda v: "     -  " if not np.isfinite(v) else "%+8.2f" % v
    print("  %-7s %-7s %s %s %s %11.0f%%" % (r.a, r.b, f(getattr(r, "_3")), f(getattr(r, "_4")), f(getattr(r, "_5")), 100 * r.neg_share))
T.to_csv("fx_opposite_pairs.csv", index=False)

# ---------------- GA over groups
rng = np.random.default_rng(7)
TR = R.loc["2017":"2021"]; TE = R.loc["2022":"2026"]
def corr(df, A, B):
    x = df[list(A)].mean(axis=1); y = df[list(B)].mean(axis=1)
    m = x.notna() & y.notna()
    return x[m].corr(y[m]) if m.sum() > 200 else 0.0
def rand_ind():
    k1, k2 = rng.integers(1, 4), rng.integers(1, 4)
    pick = rng.choice(syms, k1 + k2, replace=False)
    return (tuple(sorted(pick[:k1])), tuple(sorted(pick[k1:])))
def mutate(ind):
    A, B = list(ind[0]), list(ind[1])
    grp = A if rng.random() < 0.5 else B
    op = rng.random()
    free = [s for s in syms if s not in A + B]
    if op < 0.4 and free:
        grp[rng.integers(len(grp))] = rng.choice(free)
    elif op < 0.7 and len(grp) < 3 and free:
        grp.append(rng.choice(free))
    elif len(grp) > 1:
        grp.pop(rng.integers(len(grp)))
    return (tuple(sorted(A)), tuple(sorted(B)))
def cross(p, q):
    A = list(dict.fromkeys(list(p[0]) + list(q[0])))[:3]
    B = [s for s in dict.fromkeys(list(p[1]) + list(q[1])) if s not in A][:3]
    return (tuple(sorted(A)), tuple(sorted(B or [rng.choice([s for s in syms if s not in A])])))
cache = {}
def fit(ind):
    if ind not in cache:
        cache[ind] = -corr(TR, *ind) - 0.03 * (len(ind[0]) + len(ind[1]) - 2)   # small cost per extra pair
    return cache[ind]
pop = [rand_ind() for _ in range(120)]
for gen in range(40):
    pop = sorted(set(pop), key=fit, reverse=True)
    elite = pop[:30]
    kids = []
    while len(kids) < 90:
        p, q = elite[rng.integers(len(elite))], elite[rng.integers(len(elite))]
        c = cross(p, q) if rng.random() < 0.5 else p
        kids.append(mutate(c) if rng.random() < 0.8 else c)
    pop = elite + kids
best = sorted(set(pop), key=fit, reverse=True)
print("\nGA — groups that move opposite (searched on 2017-21, checked on 2022-26)")
print("  evaluated %d distinct groupings" % len(cache))
print("  %-28s vs %-28s %9s %9s" % ("group A", "group B", "2017-21", "2022-26"))
seen = 0
for ind in best:
    if seen == 8: break
    print("  %-28s vs %-28s %+9.2f %+9.2f" % (" + ".join(ind[0]), " + ".join(ind[1]), corr(TR, *ind), corr(TE, *ind)))
    seen += 1
