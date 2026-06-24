"""
Example: Backtesting a Scoring-Based Options Strategy

This script demonstrates how to use the backtesting module to validate
your options trading strategy against historical data.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from src.data.stocks import get_stock_snapshot, get_price_history
from src.data.options import get_options_snapshot, get_available_option_expiries
from src.analytics.probability_model import probability_from_price_series
from src.analytics.scoring_model import score_options
from src.analytics.backtest import backtest_scoring_strategy, Backtest


def main():
    """Run backtest example."""
    print("=" * 60)
    print("Options Trading Strategy Backtest")
    print("=" * 60)

    # 1. Fetch real market data
    tickers = ["AAPL"]
    print(f"\n1. Fetching data for: {tickers}")

    stocks = get_stock_snapshot(tickers)
    print(f"   Stocks: {stocks.to_dict('records')}")

    # 2. Get option expiries
    expiries = []
    for ticker in tickers:
        exp = get_available_option_expiries(ticker)
        expiries.extend(exp[:2])  # Take first 2 expiries
    expiries = list(set(expiries))[:2]
    print(f"   Using expiries: {expiries}")

    # 3. Fetch option chain
    options = get_options_snapshot(tickers, expiries)
    print(f"\n2. Fetched {len(options)} options")

    if not options.empty:
        # 4. Compute probabilities
        price_hist = {t: get_price_history(t, period="1y") for t in tickers}
        options["probability"] = options.apply(
            lambda r: probability_from_price_series(
                price_hist.get(r["ticker"], []),
                r["strike"],
                r["type"],
                days_to_expiry=30
            ),
            axis=1
        )

        # 5. Score options
        options = score_options(options)
        print(f"\n3. Computed scores and probabilities")

        # Show top 5 highest scoring options
        top_options = options.nlargest(5, "score")[
            ["ticker", "type", "strike", "price", "probability", "score"]
        ]
        print(f"\n   Top 5 Options by Score:")
        print(f"   {top_options.to_string()}")

        # 6. Run backtest
        print(f"\n4. Running backtest with score threshold=50.0...")
        backtest = backtest_scoring_strategy(
            historical_data=options,
            score_threshold=50.0,
            target_multiplier=1.5,
            stop_loss_multiplier=0.7,
        )

        # 7. Show results
        results = backtest.get_results()
        print(f"\n5. Backtest Results:")
        print(f"   Total Return: {results['total_return_pct']:.2f}%")
        print(f"   Final Capital: ${results['final_capital']:.2f}")
        print(f"   Number of Trades: {results['num_trades']}")
        print(f"   Win Rate: {results['win_rate']:.2f}%")
        print(f"   Avg Win: ${results['avg_win']:.2f}")
        print(f"   Avg Loss: ${results['avg_loss']:.2f}")
        print(f"   Max Drawdown: {results['max_drawdown']:.2f}%")

        if not results["trades"].empty:
            print(f"\n   Sample Trades:")
            print(f"   {results['trades'].head(3).to_string()}")

    print("\n" + "=" * 60)
    print("Backtest complete! Adjust score_threshold to optimize.")
    print("=" * 60)


if __name__ == "__main__":
    main()
