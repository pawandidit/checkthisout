import math
from scipy.stats import norm
import numpy as np
import pandas as pd


def compute_greeks(S, K, T, r, sigma, option_type="call"):
    """Return Black-Scholes greeks. Defensive: if inputs invalid returns zeros."""
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}

        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        if option_type == "call":
            delta = norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(d2))
            rho = K * T * math.exp(-r * T) * norm.cdf(d2)
        else:
            delta = -norm.cdf(-d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) + r * K * math.exp(-r * T) * norm.cdf(-d2))
            rho = -K * T * math.exp(-r * T) * norm.cdf(-d2)

        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * norm.pdf(d1) * math.sqrt(T)

        return {"delta": float(delta), "gamma": float(gamma), "theta": float(theta), "vega": float(vega), "rho": float(rho)}
    except Exception:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}


def probability_from_price_series(price_series, strike, option_type="CALL", days_to_expiry=30, n_sims=2000, seed=42):
    """
    Estimate probability of finishing in-the-money using historical bootstrap simulation.

    - price_series: pd.Series of historical close prices (oldest->newest)
    - strike: numeric strike price
    - option_type: "CALL" or "PUT"
    - days_to_expiry: integer days forward to simulate
    - n_sims: number of bootstrap simulations

    Returns probability as percentage (0-100) rounded to 2 decimals.
    """
    if not isinstance(price_series, (pd.Series, np.ndarray)):
        return 0.0

    if len(price_series) < 2 or days_to_expiry <= 0:
        return 0.0

    # Ensure numpy array of prices
    if isinstance(price_series, pd.Series):
        prices = price_series.dropna().values
    else:
        prices = np.asarray(price_series)

    if len(prices) < 2:
        return 0.0

    S0 = float(prices[-1])
    # compute log returns
    log_returns = np.log(prices[1:] / prices[:-1])

    rng = np.random.default_rng(seed)

    # If we have very little history, fallback to parametric normal approximation
    if len(log_returns) < 10:
        mu = np.mean(log_returns) * 252
        sigma = np.std(log_returns, ddof=1) * np.sqrt(252)
        T = days_to_expiry / 365
        if sigma <= 0:
            return 0.0
        # probability S_T > K for lognormal: 1 - Phi((ln(K/S0) - (mu-0.5*sigma^2)T)/(sigma*sqrt(T)))
        z = (math.log(strike / S0) - (mu - 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        p_call = 1 - norm.cdf(z)
        p = p_call if option_type.upper() == "CALL" else 1 - p_call
        return round(max(0.0, min(100.0, p * 100)), 2)

    # Bootstrap simulation from historical daily returns
    days = int(days_to_expiry)
    successes = 0
    n = n_sims
    # sample with replacement sums of 'days' returns
    for _ in range(n):
        sampled = rng.choice(log_returns, size=days, replace=True)
        total = sampled.sum()
        S_T = S0 * math.exp(total)
        if option_type.upper() == "CALL":
            if S_T > strike:
                successes += 1
        else:
            if S_T < strike:
                successes += 1

    prob = successes / n if n > 0 else 0.0
    return round(prob * 100, 2)
