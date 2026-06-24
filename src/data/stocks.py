import re
import yfinance as yf
import pandas as pd
import numpy as np
from src.utils.cache import cached, retry

_TICKER_RE = re.compile(r"^[A-Z0-9\.-]{1,8}$")


def _valid_ticker(ticker: str) -> bool:
    return isinstance(ticker, str) and _TICKER_RE.match(ticker.upper()) is not None


@retry(max_attempts=3, backoff_factor=1.5)
@cached(ttl_seconds=300)
def get_price_history(ticker, period="1y"):
    """Return a pandas Series of close prices for ticker. Defensive, cached, and resilient."""
    try:
        if not _valid_ticker(ticker):
            return pd.Series(dtype=float)

        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if hist is None or hist.empty:
            return pd.Series(dtype=float)

        return hist["Close"].dropna()
    except Exception:
        return pd.Series(dtype=float)


@retry(max_attempts=3, backoff_factor=1.5)
@cached(ttl_seconds=300)
def get_stock_snapshot(tickers):
    rows = []

    for ticker in tickers:
        if not _valid_ticker(ticker):
            continue

        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="3mo")

            if hist is None or hist.empty:
                continue

            price = hist["Close"].iloc[-1]
            returns = np.log(hist["Close"] / hist["Close"].shift(1)).dropna()
            vol = returns.std() * np.sqrt(252) if not returns.empty else 0.0

            rows.append({
                "ticker": ticker,
                "price": round(price, 2),
                "realized_vol": round(vol, 4)
            })
        except Exception:
            continue

    return pd.DataFrame(rows)
