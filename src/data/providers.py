"""Abstract base class for market data providers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd


class MarketDataProvider(ABC):
    """Abstract interface for market data providers."""

    @abstractmethod
    def get_stock_price(self, ticker: str) -> float:
        """Get current stock price."""
        pass

    @abstractmethod
    def get_price_history(self, ticker: str, period: str = "1y") -> pd.Series:
        """Get historical price series."""
        pass

    @abstractmethod
    def get_option_expiries(self, ticker: str) -> List[str]:
        """Get available option expiration dates."""
        pass

    @abstractmethod
    def get_option_chain(self, ticker: str, expiry: str) -> Dict[str, pd.DataFrame]:
        """Get option chain (calls and puts) for a ticker/expiry."""
        pass


class YFinanceProvider(MarketDataProvider):
    """Yahoo Finance data provider implementation."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._setup()

    def _setup(self):
        """Setup provider."""
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            raise ImportError("yfinance not installed. Install with: pip install yfinance")

    def get_stock_price(self, ticker: str) -> float:
        """Get current stock price from Yahoo Finance."""
        try:
            ticker_obj = self.yf.Ticker(ticker)
            data = ticker_obj.history(period="1d")
            if data.empty:
                return 0.0
            return float(data["Close"].iloc[-1])
        except Exception:
            return 0.0

    def get_price_history(self, ticker: str, period: str = "1y") -> pd.Series:
        """Get historical prices from Yahoo Finance."""
        try:
            ticker_obj = self.yf.Ticker(ticker)
            hist = ticker_obj.history(period=period)
            if hist is None or hist.empty:
                return pd.Series(dtype=float)
            return hist["Close"].dropna()
        except Exception:
            return pd.Series(dtype=float)

    def get_option_expiries(self, ticker: str) -> List[str]:
        """Get option expirations from Yahoo Finance."""
        try:
            ticker_obj = self.yf.Ticker(ticker)
            return ticker_obj.options if ticker_obj.options else []
        except Exception:
            return []

    def get_option_chain(self, ticker: str, expiry: str) -> Dict[str, pd.DataFrame]:
        """Get option chain from Yahoo Finance."""
        try:
            ticker_obj = self.yf.Ticker(ticker)
            chain = ticker_obj.option_chain(expiry)
            return {"calls": chain.calls, "puts": chain.puts}
        except Exception:
            return {"calls": pd.DataFrame(), "puts": pd.DataFrame()}


# Factory function to create provider
def get_data_provider(provider_name: str = "yfinance", **kwargs) -> MarketDataProvider:
    """Factory to create market data provider."""
    providers = {
        "yfinance": YFinanceProvider,
    }

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(providers.keys())}")

    return providers[provider_name](**kwargs)
