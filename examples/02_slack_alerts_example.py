"""
Example: Setting Up Slack Alerts for Trading Signals

This script demonstrates how to configure and send trading alerts to Slack.

Setup:
1. Create a Slack workspace (or use existing)
2. Create an Incoming Webhook: https://api.slack.com/messaging/webhooks
3. Copy the webhook URL
4. Set SLACK_WEBHOOK_URL in .env or as environment variable
5. Run this script
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from src.utils.alerting import SlackAlerter
from src.data.stocks import get_stock_snapshot
from src.data.options import get_options_snapshot, get_available_option_expiries
from src.analytics.probability_model import probability_from_price_series
from src.analytics.scoring_model import score_options
from src.data.stocks import get_price_history


def main():
    """Run Slack alerts example."""
    print("=" * 60)
    print("Slack Trading Alerts Example")
    print("=" * 60)

    # Initialize alerter
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("\n⚠️  SLACK_WEBHOOK_URL not set.")
        print("   Create a webhook: https://api.slack.com/messaging/webhooks")
        print("   Then set: export SLACK_WEBHOOK_URL='your-webhook-url'")
        print("\n   Continuing with demo (alerts will not be sent)...\n")

    alerter = SlackAlerter(webhook_url=webhook_url)

    # 1. Fetch market data
    print("1. Fetching market data...")
    tickers = ["AAPL"]
    stocks = get_stock_snapshot(tickers)
    
    expiries = []
    for ticker in tickers:
        exp = get_available_option_expiries(ticker)
        expiries.extend(exp[:2])
    expiries = list(set(expiries))[:2]

    options = get_options_snapshot(tickers, expiries)

    if not options.empty:
        # 2. Compute probabilities
        print("2. Computing probabilities...")
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

        # 3. Score options
        print("3. Scoring options...")
        options = score_options(options)

        # 4. Send alerts for high-probability options
        print("4. Sending Slack alerts for high-probability options...\n")
        
        high_prob_options = options[options["probability"] > 60].head(3)
        
        for idx, option in high_prob_options.iterrows():
            print(f"   Alerting: {option['ticker']} {option['type']} ${option['strike']:.0f} "
                  f"(Prob: {option['probability']:.1f}%)")
            alerter.alert_high_probability_option(option)

        # 5. Send a portfolio summary alert
        print("\n5. Sending portfolio summary alert...")
        portfolio_metrics = {
            "pnl": 1250.50,
            "return_pct": 12.5,
            "num_positions": 3
        }
        alerter.alert_portfolio(portfolio_metrics)

        # 6. Send a trading signal alert
        print("\n6. Sending trading signal alert...")
        alerter.alert_signal("BUY", "Strong technical setup on AAPL Call spread")

    print("\n" + "=" * 60)
    print("Alert examples sent! Check your Slack channel.")
    print("=" * 60)


if __name__ == "__main__":
    main()
