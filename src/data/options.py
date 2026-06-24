import yfinance as yf
import pandas as pd
from src.utils.cache import cached, retry


@retry(max_attempts=3, backoff_factor=1.5)
@cached(ttl_seconds=300)
def get_available_option_expiries(ticker):
    try:
        return yf.Ticker(ticker).options
    except Exception:
        return []


@retry(max_attempts=3, backoff_factor=1.5)
@cached(ttl_seconds=300)
def get_options_snapshot(tickers, expiries):
    rows = []

    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)

            for expiry in expiries:
                if expiry not in t.options:
                    continue

                chain = t.option_chain(expiry)

                for side, df in [("CALL", chain.calls), ("PUT", chain.puts)]:
                    for _, r in df.iterrows():
                        if r["lastPrice"] <= 0:
                            continue

                        rows.append({
                            "ticker": ticker,
                            "expiry": expiry,
                            "type": side,
                            "strike": r["strike"],
                            "price": r["lastPrice"],
                            "delta": abs(r.get("delta", 0)),
                            "gamma": r.get("gamma", 0),
                            "theta": abs(r.get("theta", 0)),
                            "vega": r.get("vega", 0),
                            "rho": r.get("rho", 0),
                            "volume": r.get("volume", 0)
                        })
        except Exception:
            continue

    return pd.DataFrame(rows)
