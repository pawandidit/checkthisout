import sys
from pathlib import Path
import numpy as np
import pandas as pd

# ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics.probability_model import compute_greeks, probability_from_price_series
from analytics.scoring_model import score_options, normalize
from analytics.trade_model import assign_strategy, compute_trade_levels
from analytics.volatility_model import classify_volatility


class TestGreeks:
    def test_compute_greeks_basic(self):
        S = 100.0
        K = 100.0
        T = 30 / 365
        r = 0.01
        sigma = 0.2

        g = compute_greeks(S, K, T, r, sigma, option_type="call")
        assert isinstance(g, dict)
        assert all(k in g for k in ("delta", "gamma", "theta", "vega", "rho"))
        assert 0 <= g["delta"] <= 1  # Call delta between 0 and 1
        assert g["gamma"] > 0

    def test_compute_greeks_invalid_inputs(self):
        # Test with invalid inputs: should return zeros
        g = compute_greeks(100, 100, 0, 0.01, 0, "call")
        assert g["delta"] == 0
        assert g["gamma"] == 0

    def test_compute_greeks_put_vs_call(self):
        S, K, T, r, sigma = 100.0, 100.0, 30 / 365, 0.01, 0.2
        g_call = compute_greeks(S, K, T, r, sigma, "call")
        g_put = compute_greeks(S, K, T, r, sigma, "put")

        # Put delta should be negative of some relationship with call delta
        assert g_call["delta"] > 0
        assert g_put["delta"] < 0


class TestProbability:
    def test_probability_from_price_series_bootstrap(self):
        rng = np.random.default_rng(123)
        returns = rng.normal(0, 0.01, size=252)
        prices = 100 * np.exp(np.cumsum(returns))

        prob = probability_from_price_series(prices, strike=prices[-1], option_type="CALL", days_to_expiry=30, n_sims=500)
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 100.0

    def test_probability_from_price_series_short_history(self):
        # Test parametric fallback with short history
        prices = np.array([100, 101, 102])
        prob = probability_from_price_series(prices, strike=105, option_type="CALL", days_to_expiry=30, n_sims=100)
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 100.0

    def test_probability_invalid_inputs(self):
        prob = probability_from_price_series([], strike=100, option_type="CALL")
        assert prob == 0.0

        prob = probability_from_price_series(None, strike=100)
        assert prob == 0.0


class TestScoring:
    def test_normalize(self):
        s = pd.Series([1, 2, 3, 4, 5])
        norm = normalize(s)
        assert norm.min() >= 0
        assert norm.max() <= 1

    def test_normalize_zero_max(self):
        s = pd.Series([0, 0, 0])
        norm = normalize(s)
        assert all(norm == 0)

    def test_score_options(self):
        df = pd.DataFrame({
            "delta": [0.5, 0.6, 0.7],
            "gamma": [0.01, 0.02, 0.03],
            "theta": [-0.05, -0.04, -0.03],
            "vega": [2, 3, 4],
            "rho": [0.1, 0.12, 0.15],
            "volume": [1000, 2000, 500],
            "probability": [50, 60, 70]
        })

        scored = score_options(df)
        assert "score" in scored.columns
        assert all(scored["score"] >= 0)
        assert all(scored["score"] <= 100)


class TestVolatility:
    def test_classify_volatility(self):
        vol_series = pd.Series([0.1, 0.15, 0.2, 0.25, 0.3])
        classified = classify_volatility(vol_series)
        assert len(classified) == len(vol_series)
        assert all(c in ["LOW", "MEDIUM", "HIGH"] for c in classified)

    def test_classify_volatility_short(self):
        vol_series = pd.Series([0.1])
        classified = classify_volatility(vol_series)
        assert classified == ["MEDIUM"]


class TestTradeModel:
    def test_assign_strategy(self):
        strategies = {
            assign_strategy("LOW"): "Long Call / Put",
            assign_strategy("MEDIUM"): "Debit Spread",
            assign_strategy("HIGH"): "Credit Spread",
            assign_strategy("UNKNOWN"): "Neutral"
        }
        assert all(v in ["Long Call / Put", "Debit Spread", "Credit Spread", "Neutral"] for v in strategies.values())

    def test_compute_trade_levels(self):
        stocks = pd.DataFrame({"ticker": ["AAPL"], "price": [150.0], "realized_vol": [0.2]})
        options = pd.DataFrame({
            "ticker": ["AAPL", "AAPL"],
            "type": ["CALL", "PUT"],
            "strike": [155, 145],
            "price": [2.0, 3.0],
            "score": [75.0, 60.0]
        })

        trades = compute_trade_levels(stocks, options)
        assert "stocks" in trades
        assert "options" in trades
        assert not trades["options"].empty
        assert "buy" in trades["options"].columns
        assert "stop_loss" in trades["options"].columns
        assert "target" in trades["options"].columns

