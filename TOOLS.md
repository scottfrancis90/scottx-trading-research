# Tools

Private tools built and used alongside this research. They are **not published and not for sale**. The exact rules stay private.

If anything here is worth discussing, open a thread in [Discussions](../../discussions).

## MetaTrader 5 Expert Advisors

| EA | Market | What it does |
|---|---|---|
| **StraddleX** | Gold (XAUUSD) | The first strategy in the study to pass a pre-registered holdout. |
| **AsianRangeX** | Forex | Trades the Asian session range into London. |
| **AsiaGoldX** | Gold | Session-based gold strategy. |
| **EURCHF_FadeX** | EURCHF | Mean-reversion strategy on EURCHF, H1. |
| **FastOBX** | Forex and gold, H4/H1 | Order-block strategy. |
| **LiquidityAlertX** | Any symbol | Alerts when daily liquidity is swept. Signals only, never trades. |

## TradingView indicators

| Indicator | What it shows |
|---|---|
| **LondonSweep** | Order blocks, breaker blocks, previous day high/low and the Asian range. |
| **LiquidityX** | Liquidity levels and sweep flags on any timeframe. |
| **FastOB** | Order blocks with entries, stops and trade results. |

Every tool was tested with the same method as the findings in this repository: random-entry control, both halves of the history, and real spreads.
