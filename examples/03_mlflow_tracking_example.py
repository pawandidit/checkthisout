"""
Example: Tracking Models and Experiments with MLflow

This script demonstrates how to use MLflow to track your options trading
experiments, parameters, and results.

Setup:
1. Install MLflow: pip install mlflow
2. Start MLflow server (optional): mlflow ui --host 0.0.0.0 --port 5000
3. View dashboard at: http://localhost:5000
"""
import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from src.utils.mlflow_tracker import get_tracker
from src.data.stocks import get_stock_snapshot, get_price_history
from src.data.options import get_options_snapshot, get_available_option_expiries
from src.analytics.probability_model import probability_from_price_series
from src.analytics.scoring_model import score_options
from src.analytics.backtest import backtest_scoring_strategy


def main():
    """Run MLflow tracking example."""
    print("=" * 60)
    print("MLflow Model Tracking Example")
    print("=" * 60)

    # Initialize tracker
    tracker = get_tracker(experiment_name="options-trading-v1")
    
    print("\n1. Starting MLflow experiment...")
    run_id = tracker.start_run(run_name="scoring_strategy_v1")
    
    if not run_id:
        print("   ⚠️  MLflow not available. Install with: pip install mlflow")
        print("   Continuing without tracking...\n")
    else:
        print(f"   Run ID: {run_id}\n")

    # Log configuration parameters
    print("2. Logging strategy parameters...")
    strategy_params = {
        "score_threshold": 50.0,
        "target_multiplier": 1.5,
        "stop_loss_multiplier": 0.7,
        "lookback_period": "1y",
        "probability_simulations": 2000
    }
    tracker.log_params(strategy_params)

    # Fetch market data
    print("3. Fetching market data...")
    tickers = ["AAPL"]
    stocks = get_stock_snapshot(tickers)
    
    expiries = []
    for ticker in tickers:
        exp = get_available_option_expiries(ticker)
        expiries.extend(exp[:2])
    expiries = list(set(expiries))[:2]

    options = get_options_snapshot(tickers, expiries)

    if not options.empty:
        # Compute probabilities and scores
        print("4. Computing analytics...")
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
        options = score_options(options)

        # Run backtest
        print("5. Running backtest...")
        backtest = backtest_scoring_strategy(
            historical_data=options,
            score_threshold=50.0,
            target_multiplier=1.5,
            stop_loss_multiplier=0.7,
        )

        results = backtest.get_results()

        # Log backtest results
        print("6. Logging backtest results...")
        tracker.log_backtest_results(results)

        # Log additional metrics
        print("7. Logging additional metrics...")
        additional_metrics = {
            "num_options_analyzed": len(options),
            "pct_options_above_threshold": (
                len(options[options["score"] >= 50]) / len(options) * 100
                if len(options) > 0 else 0
            ),
            "avg_probability": options["probability"].mean(),
            "avg_score": options["score"].mean(),
        }
        tracker.log_metrics(additional_metrics)

        print(f"\n8. Results Summary:")
        print(f"   Total Return: {results['total_return_pct']:.2f}%")
        print(f"   Win Rate: {results['win_rate']:.2f}%")
        print(f"   Max Drawdown: {results['max_drawdown']:.2f}%")
        print(f"   Number of Trades: {results['num_trades']}")

    # End run
    print(f"\n9. Ending MLflow run...")
    tracker.end_run()

    print("\n" + "=" * 60)
    print("Experiment logged! View results at:")
    print("  Local: ./mlruns or open MLflow UI")
    print("=" * 60)


if __name__ == "__main__":
    main()
