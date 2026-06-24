"""Slack alerting integration for trading signals."""
import os
import logging
from typing import Optional, Dict, Any
from urllib.request import Request, urlopen
import json

logger = logging.getLogger(__name__)


class SlackAlerter:
    """Send trading alerts to Slack."""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack alerter.

        Args:
            webhook_url: Slack incoming webhook URL. If None, uses SLACK_WEBHOOK_URL env var.
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

        if not self.webhook_url:
            logger.warning("No Slack webhook URL provided. Alerting disabled.")

    def send_alert(self, title: str, message: str, color: str = "#36a64f") -> bool:
        """
        Send a formatted message to Slack.

        Args:
            title: Alert title
            message: Alert message
            color: Hex color code for message block

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            return False

        try:
            payload = {
                "attachments": [
                    {
                        "fallback": f"{title}: {message}",
                        "color": color,
                        "title": title,
                        "text": message,
                        "ts": int(os.times()[4]),  # current time
                    }
                ]
            }

            data = json.dumps(payload).encode("utf-8")
            req = Request(self.webhook_url, data=data, headers={"Content-Type": "application/json"})

            with urlopen(req) as response:
                result = response.read()
                if response.status == 200:
                    logger.info(f"Slack alert sent: {title}")
                    return True
                else:
                    logger.error(f"Failed to send Slack alert: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False

    def alert_high_probability_option(self, option: Dict[str, Any]) -> bool:
        """Alert when a high-probability option is found."""
        ticker = option.get("ticker", "UNKNOWN")
        strike = option.get("strike", 0)
        option_type = option.get("type", "CALL")
        probability = option.get("probability", 0)
        score = option.get("score", 0)
        price = option.get("price", 0)

        title = f"🎯 High Probability {option_type} Option: {ticker}"
        message = (
            f"Strike: ${strike:.0f}\n"
            f"Price: ${price:.2f}\n"
            f"Probability: {probability:.1f}%\n"
            f"Score: {score:.1f}"
        )
        color = "#36a64f" if probability > 60 else "#ffa500"  # Green if prob > 60%, orange otherwise

        return self.send_alert(title, message, color)

    def alert_signal(self, signal_type: str, details: str) -> bool:
        """Alert for trading signals."""
        title = f"📊 {signal_type}"
        color_map = {
            "BUY": "#36a64f",
            "SELL": "#ff0000",
            "NEUTRAL": "#ffa500",
        }
        color = color_map.get(signal_type.upper(), "#36a64f")

        return self.send_alert(title, details, color)

    def alert_portfolio(self, portfolio_metrics: Dict[str, Any]) -> bool:
        """Alert with portfolio metrics."""
        pnl = portfolio_metrics.get("pnl", 0)
        return_pct = portfolio_metrics.get("return_pct", 0)
        num_positions = portfolio_metrics.get("num_positions", 0)

        title = "💼 Portfolio Update"
        message = (
            f"P&L: ${pnl:.2f}\n"
            f"Return: {return_pct:.2f}%\n"
            f"Positions: {num_positions}"
        )
        color = "#36a64f" if pnl > 0 else "#ff0000"

        return self.send_alert(title, message, color)


# Factory function
def get_alerter() -> SlackAlerter:
    """Get Slack alerter instance."""
    return SlackAlerter()
