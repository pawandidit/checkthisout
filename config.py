import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Data Provider Configuration
DATA_PROVIDER = os.getenv("DATA_PROVIDER", "yfinance")
MARKET_DATA_CACHE_TTL = int(os.getenv("MARKET_DATA_CACHE_TTL", "300"))

# Dashboard Configuration
DASH_HOST = os.getenv("DASH_HOST", "0.0.0.0")
DASH_PORT = int(os.getenv("DASH_PORT", "8050"))
DASH_DEBUG = os.getenv("DASH_DEBUG", "True").lower() == "true"
REFRESH_INTERVAL_MS = int(os.getenv("REFRESH_INTERVAL_MS", "30000"))

# Trading Configuration
MAX_TICKERS = int(os.getenv("MAX_TICKERS", "5"))
DEFAULT_LOOKBACK_PERIOD = os.getenv("DEFAULT_LOOKBACK_PERIOD", "1y")
DEFAULT_OPTION_DAYS_TO_EXPIRY = int(os.getenv("DEFAULT_OPTION_DAYS_TO_EXPIRY", "30"))

# Analysis Configuration
VOLATILITY_CLUSTERS = int(os.getenv("VOLATILITY_CLUSTERS", "3"))
PROBABILITY_SIMULATIONS = int(os.getenv("PROBABILITY_SIMULATIONS", "2000"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# Scoring Weights
SCORE_WEIGHTS = {
    "delta": 0.25,
    "gamma": 0.10,
    "theta": 0.15,
    "vega": 0.20,
    "rho": 0.05,
    "volume": 0.10,
    "probability": 0.15
}

# Risk Management
MAX_LEVERAGE = float(os.getenv("MAX_LEVERAGE", "2.0"))
POSITION_SIZE_PCT = float(os.getenv("POSITION_SIZE_PCT", "2.0"))
STOP_LOSS_PCTS = float(os.getenv("STOP_LOSS_PCTS", "0.7"))
TAKE_PROFIT_PCTS = float(os.getenv("TAKE_PROFIT_PCTS", "1.6"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE) if os.path.dirname(LOG_FILE) else ".", exist_ok=True)
