# Methodology

How the tests in this repository are designed, and the mistakes that shaped the design.

## 1. Write the rule first

Each test starts from a rule written in full before any result is seen: entry, stop, exit, timeframe, instruments, period. When a rule is ambiguous, the interpretation is stated in the finding. Changing the rule after looking at the result makes a new test, and it is counted as one.

## 2. Compare with random entries

A strategy's average result means nothing on its own. Gold rose for most of 2017-2026, so almost any buy rule looks profitable. Each strategy is therefore compared with **random entries** on the same instrument, in the same year, in the same direction, with the same stop distance and the same exit. The difference is the edge. Many results in this repo that looked positive were the market's drift and nothing else.

## 3. Report both halves

Every result is reported separately for 2017-2021 and 2022-2026. A rule that works in one half and fails in the other is not treated as working.

## 4. Use the real cost

The spread recorded at the time of each trade is charged, not today's spread (spreads were several times wider in 2017-2018 on some instruments). On M1 and M5 the spread is often larger than the edge.

## 5. No lookahead, including the hidden kinds

The usual lookahead (a feature using a future bar) is easy to avoid. The ones that cost the most time here were subtler:

- **Intrabar ordering.** On an H4 candle you cannot know whether the high or the low came first. A trailing stop or a position add credited inside the same candle can create profit that never existed. Trades are replayed on lower-timeframe candles (H4 on H1, H1 on M30), and a stop and a target touched in the same candle count as the stop.
- **Selection lookahead.** A rule can use only past data for its signal and still look into the future through **which** bars it is allowed to trade. This passed every control and a pre-registered holdout before it was found ([Finding 77](../findings/077-the-ga-survivor-was-lookahead-in-the-signal-generator-findings-75-and-.md)).
- **Order of fills.** Overlapping pending orders must fill in time order, not signal order ([Finding 83](../findings/083-defect-12-overlapping-pending-orders-were-filling-in-signal-order-not-.md)).

## 6. Count the attempts

Every variant tried is logged. When fifty versions of an idea have been tested, the best of them is expected to look good by chance, and it is judged against that.

## 7. Win rate is not the target

A high win rate with small winners and occasional large losers is the most common way a strategy looks good and loses money. Results are judged on average result per trade in units of risk (R), drawdown, and stability across years, pairs and the two halves.
