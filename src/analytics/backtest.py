"""Backtesting module for options trading strategies."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable


class Backtest:
    """Simple options backtesting engine."""

    def __init__(
        self,
        starting_capital: float = 10000.0,
        transaction_cost: float = 0.001,  # 0.1% per trade
    ):
        self.starting_capital = starting_capital
        self.capital = starting_capital
        self.transaction_cost = transaction_cost
        self.trades = []
        self.equity_curve = [starting_capital]
        self.dates = []

    def add_trade(
        self,
        date: datetime,
        ticker: str,
        option_type: str,
        strike: float,
        entry_price: float,
        exit_price: float,
        quantity: int = 1,
    ) -> Dict[str, Any]:
        """Record a trade execution."""
        gross_pnl = (exit_price - entry_price) * quantity * 100  # options are 100x
        costs = (entry_price + exit_price) * quantity * 100 * self.transaction_cost
        net_pnl = gross_pnl - costs

        self.capital += net_pnl
        self.equity_curve.append(self.capital)
        self.dates.append(date)

        trade_record = {
            "date": date,
            "ticker": ticker,
            "type": option_type,
            "strike": strike,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "gross_pnl": gross_pnl,
            "costs": costs,
            "net_pnl": net_pnl,
            "total_capital": self.capital,
            "return_pct": (net_pnl / (entry_price * quantity * 100)) * 100 if entry_price > 0 else 0,
        }

        self.trades.append(trade_record)
        return trade_record

    def get_results(self) -> Dict[str, Any]:
        """Get backtest results summary."""
        if not self.trades:
            return {
                "total_return_pct": 0.0,
                "num_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "max_drawdown": 0.0,
            }

        trades_df = pd.DataFrame(self.trades)

        # Calculate metrics
        total_return = ((self.capital - self.starting_capital) / self.starting_capital) * 100
        num_trades = len(self.trades)
        winning_trades = trades_df[trades_df["net_pnl"] > 0]
        losing_trades = trades_df[trades_df["net_pnl"] < 0]

        win_rate = (len(winning_trades) / num_trades * 100) if num_trades > 0 else 0
        avg_win = winning_trades["net_pnl"].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades["net_pnl"].mean() if len(losing_trades) > 0 else 0

        # Calculate max drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max * 100
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0

        return {
            "total_return_pct": round(total_return, 2),
            "final_capital": round(self.capital, 2),
            "num_trades": num_trades,
            "win_rate": round(win_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "max_drawdown": round(max_drawdown, 2),
            "trades": trades_df,
        }


def backtest_scoring_strategy(
    historical_data: pd.DataFrame,
    score_threshold: float = 50.0,
    target_multiplier: float = 1.5,
    stop_loss_multiplier: float = 0.7,
) -> Backtest:
    """
    Backtest a simple scoring-based options strategy.

    Args:
        historical_data: DataFrame with historical option prices and scores
        score_threshold: Minimum score to enter trade
        target_multiplier: Price target multiplier from entry
        stop_loss_multiplier: Stop-loss multiplier from entry

    Returns:
        Backtest object with results
    """
    bt = Backtest(starting_capital=10000.0)

    if historical_data.empty or "score" not in historical_data.columns:
        return bt

    # Filter for high-scoring options
    high_score_options = historical_data[historical_data["score"] >= score_threshold]

    for idx, option in high_score_options.iterrows():
        # Simple strategy: buy high-score options, exit at target or stop
        entry_price = option.get("price", 0)
        if entry_price <= 0:
            continue

        target_price = entry_price * target_multiplier
        stop_price = entry_price * stop_loss_multiplier

        # Simulate exit (simplified: assume random close between stop and target)
        exit_price = np.random.uniform(stop_price, target_price)

        trade_date = option.get("date", datetime.now())
        ticker = option.get("ticker", "UNKNOWN")
        option_type = option.get("type", "CALL")
        strike = option.get("strike", 0)

        bt.add_trade(
            date=trade_date,
            ticker=ticker,
            option_type=option_type,
            strike=strike,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=1,
        )

    return bt
