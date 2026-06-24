# Financial ML - Options Intelligence Dashboard

A production-ready options trading analytics dashboard powered by machine learning and quantitative analysis.

## 🚀 Features

- **📊 Real-Time Data:** Fetch stock prices and option chains from Yahoo Finance (or swap providers)
- **🎯 Advanced Analytics:**
  - Black-Scholes Greeks (delta, gamma, theta, vega, rho)
  - Historical-simulation probability estimates using bootstrap methods
  - Volatility classification (LOW/MEDIUM/HIGH) via KMeans clustering
  - Composite scoring based on weighted greeks and probability
- **📈 Smart Trade Recommendations:** Automated trade levels (buy, stop-loss, target)
- **🔍 Search & Filter:** Real-time search across tickers, strikes, and types
- **⭐ Probability Sorting:** Options automatically sorted by probability of profit
- **📚 Backtesting:** Validate trading strategies against historical data
- **📢 Slack Alerts:** Real-time notifications for high-probability options
- **📊 MLflow Tracking:** Track experiments, parameters, and model performance
- **🔌 Pluggable Data Providers:** Easy swap between yfinance, Polygon, IEX, etc.
- **🛡️ Production-Ready:**
  - Input validation and defensive error handling
  - Request caching (5-minute TTL) and exponential backoff retries
  - Comprehensive unit tests
  - Docker containerization
  - .env-based configuration

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Examples](#examples)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or conda

### 1. Clone & Install

```bash
git clone <repo-url>
cd financial-ml
pip install -r requirements.txt
cp .env.example .env  # Copy configuration template
```

### 2. Run the Dashboard

```bash
python app.py
```

Open your browser to **http://localhost:8050**

### 3. Run Tests

```bash
python -m pytest tests/ -v
```

## 🐳 Docker Setup

### Build & Run

```bash
docker-compose up --build
```

The dashboard will be available at **http://localhost:8050**

### Rebuild Image

```bash
docker-compose up --build --remove-orphans
```

### Stop

```bash
docker-compose down
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Key Settings:**

```env
# Data Provider: "yfinance" (default), "polygon", "iex", "tradier"
DATA_PROVIDER=yfinance

# Slack Notifications (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# MLflow Tracking (optional)
MLFLOW_TRACKING_URI=./mlruns

# Dashboard
DASH_HOST=0.0.0.0
DASH_PORT=8050
DASH_DEBUG=True

# Analysis Parameters
VOLATILITY_CLUSTERS=3
PROBABILITY_SIMULATIONS=2000
DEFAULT_OPTION_DAYS_TO_EXPIRY=30

# Caching
MARKET_DATA_CACHE_TTL=300
```

### Python Config

Edit `config.py` to customize scoring weights:

```python
SCORE_WEIGHTS = {
    "delta": 0.25,      # Directional exposure
    "gamma": 0.10,      # Acceleration
    "theta": 0.15,      # Time decay
    "vega": 0.20,       # Volatility sensitivity
    "rho": 0.05,        # Interest rate
    "volume": 0.10,     # Liquidity
    "probability": 0.15 # Probability of profit
}
```

## 📖 Examples

Run practical examples in the `examples/` directory:

### 1. Backtesting Strategies

```bash
python examples/01_backtest_example.py
```

**Features:**
- Fetch real market data
- Compute option scores and probabilities
- Run backtest with configurable thresholds
- View P&L, win rate, and drawdown metrics

**Code:**
```python
from src.analytics.backtest import backtest_scoring_strategy

backtest = backtest_scoring_strategy(
    historical_data=options,
    score_threshold=50.0,
    target_multiplier=1.5,
    stop_loss_multiplier=0.7
)

results = backtest.get_results()
print(f"Total Return: {results['total_return_pct']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
```

### 2. Slack Alerts

```bash
# Set your Slack webhook URL
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

python examples/02_slack_alerts_example.py
```

**Features:**
- Alert on high-probability options
- Portfolio metrics notifications
- Trading signal alerts

**Code:**
```python
from src.utils.alerting import SlackAlerter

alerter = SlackAlerter()
alerter.alert_high_probability_option({
    "ticker": "AAPL",
    "type": "CALL",
    "strike": 175.0,
    "probability": 75.5,
    "price": 2.50
})
```

### 3. MLflow Model Tracking

```bash
# Install MLflow (optional)
pip install mlflow

# Start MLflow UI (optional)
mlflow ui --host 0.0.0.0 --port 5000

# Run tracking example
python examples/03_mlflow_tracking_example.py
```

**Features:**
- Track experiment parameters
- Log backtest results
- Compare model performance
- View results at http://localhost:5000

**Code:**
```python
from src.utils.mlflow_tracker import get_tracker

tracker = get_tracker()
tracker.start_run(run_name="my_strategy_v1")
tracker.log_params({"score_threshold": 50.0})
tracker.log_metrics({"total_return": 12.5})
tracker.end_run()
```

### 4. Using Different Data Providers

```bash
python examples/04_data_providers_example.py
```

**Swap Data Providers:**

```python
from src.data.providers import get_data_provider

# Use yfinance (default)
provider = get_data_provider("yfinance")

# Get market data through provider interface
price = provider.get_stock_price("AAPL")
history = provider.get_price_history("AAPL", period="1y")
expiries = provider.get_option_expiries("AAPL")
chain = provider.get_option_chain("AAPL", "2024-06-21")
```

**Implementing Custom Providers:**

```python
from src.data.providers import MarketDataProvider

class PolygonProvider(MarketDataProvider):
    def get_stock_price(self, ticker: str) -> float:
        # Implement using Polygon API
        pass
    
    def get_price_history(self, ticker: str, period: str) -> pd.Series:
        # Implement using Polygon API
        pass
    
    # ... implement other methods
```

## 🏗️ Architecture

```
financial-ml/
├── app.py                          # Dash entry point
├── config.py                       # Configuration & env loading
├── requirements.txt                # Dependencies
├── Dockerfile                      # Container image
├── docker-compose.yml              # Local dev setup
├── .env.example                    # Configuration template
│
├── src/
│   ├── analytics/                  # Core analytics
│   │   ├── probability_model.py    # Greeks & probability simulation
│   │   ├── scoring_model.py        # Composite option scoring
│   │   ├── trade_model.py          # Trade level computation
│   │   ├── volatility_model.py     # Vol classification
│   │   └── backtest.py             # Strategy backtesting
│   │
│   ├── data/                       # Market data
│   │   ├── providers.py            # Abstract provider interface
│   │   ├── stocks.py               # Stock snapshot & price history
│   │   └── options.py              # Option chain fetching
│   │
│   ├── dashboard/                  # UI & interactions
│   │   ├── layout.py               # Beautiful responsive layout
│   │   └── callbacks.py            # Dash callbacks with search/sort
│   │
│   └── utils/
│       ├── cache.py                # Caching & retry decorators
│       ├── alerting.py             # Slack alert integration
│       └── mlflow_tracker.py       # MLflow model tracking
│
├── tests/
│   └── test_analytics.py           # Comprehensive unit tests
│
├── examples/
│   ├── 01_backtest_example.py      # Backtesting example
│   ├── 02_slack_alerts_example.py  # Slack alerting example
│   ├── 03_mlflow_tracking_example.py  # MLflow tracking example
│   └── 04_data_providers_example.py   # Data providers example
│
└── .github/
    └── workflows/
        └── test.yml                # GitHub Actions CI pipeline
```

## 🔌 API Reference

### Market Data

```python
from src.data.stocks import get_stock_snapshot, get_price_history
from src.data.options import get_available_option_expiries, get_options_snapshot

# Get stock snapshot (price & realized volatility)
stocks = get_stock_snapshot(["AAPL", "NVDA"])

# Get historical prices
prices = get_price_history("AAPL", period="1y")

# Get option expiries
expiries = get_available_option_expiries("AAPL")

# Get option chain
options = get_options_snapshot(["AAPL"], expiries)
```

### Analytics

```python
from src.analytics.probability_model import probability_from_price_series, compute_greeks
from src.analytics.scoring_model import score_options
from src.analytics.volatility_model import classify_volatility

# Estimate probability using historical prices
prob = probability_from_price_series(
    price_series=prices,
    strike=175.0,
    option_type="CALL",
    days_to_expiry=30,
    n_sims=2000
)

# Compute Black-Scholes Greeks
greeks = compute_greeks(
    S=175.0,
    K=180.0,
    T=30/365,
    r=0.05,
    sigma=0.25,
    option_type="call"
)

# Score options
scored = score_options(options)

# Classify volatility
vol_regimes = classify_volatility(stocks["realized_vol"])
```

### Backtesting

```python
from src.analytics.backtest import backtest_scoring_strategy

backtest = backtest_scoring_strategy(
    historical_data=options,
    score_threshold=50.0,
    target_multiplier=1.5,
    stop_loss_multiplier=0.7
)

results = backtest.get_results()
```

### Alerting

```python
from src.utils.alerting import SlackAlerter

alerter = SlackAlerter()
alerter.alert_high_probability_option(option_dict)
alerter.alert_signal("BUY", "Strong setup on AAPL")
alerter.alert_portfolio({"pnl": 1250, "return_pct": 12.5})
```

### MLflow Tracking

```python
from src.utils.mlflow_tracker import get_tracker

tracker = get_tracker()
tracker.start_run(run_name="my_strategy")
tracker.log_params({"threshold": 50.0})
tracker.log_metrics({"return": 12.5})
tracker.log_backtest_results(backtest_results)
tracker.end_run()
```

## 🌐 Deployment

### Local Development
```bash
pip install -r requirements.txt
python app.py  # http://localhost:8050
```

### Docker (Recommended)
```bash
docker-compose up --build
```

### AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 20.04)
# 2. SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# 3. Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# 4. Clone repo and run
git clone <repo-url>
cd financial-ml
docker-compose up -d

# 5. Access at http://your-instance-ip:8050
```

### AWS ECS (Fargate)

```bash
# 1. Build and push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <YOUR_ECR_URI>
docker build -t financial-ml .
docker tag financial-ml <YOUR_ECR_URI>/financial-ml:latest
docker push <YOUR_ECR_URI>/financial-ml:latest

# 2. Create ECS task definition, service, and cluster via AWS Console or CLI

# 3. Access via load balancer URL
```

### AWS Lambda + API Gateway

```bash
# For serverless option snapshots only (not full dashboard)
pip install zappa
zappa init
zappa deploy dev
```

### Google Cloud Run

```bash
# 1. Setup GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Build and deploy
gcloud run deploy financial-ml \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8050
```

### Google Cloud Compute Engine

```bash
# 1. Create instance
gcloud compute instances create financial-ml \
  --image-family ubuntu-2004-lts \
  --image-project ubuntu-os-cloud

# 2. SSH and deploy
gcloud compute ssh financial-ml
git clone <repo-url>
cd financial-ml
docker-compose up -d
```

### Heroku

```bash
# 1. Install Heroku CLI
# 2. Create Procfile
echo "web: python app.py" > Procfile

# 3. Create and deploy
heroku create your-app-name
heroku config:set DASH_HOST=0.0.0.0 DASH_PORT=8050
git push heroku main

# 4. View logs
heroku logs -t
```

### Railway.app

```bash
# 1. Connect GitHub repo on Railway
# 2. Set environment variables in Railway console
# 3. Deploy automatically on push
```

### DigitalOcean App Platform

```bash
# 1. Create new app on DO
# 2. Connect GitHub repo
# 3. Set build command: pip install -r requirements.txt
# 4. Set start command: python app.py
# 5. Deploy
```

### Kubernetes (Helm)

```bash
# 1. Build Docker image
docker build -t financial-ml:latest .

# 2. Push to registry
docker tag financial-ml myregistry/financial-ml:latest
docker push myregistry/financial-ml:latest

# 3. Deploy with kubectl
kubectl create deployment financial-ml --image=myregistry/financial-ml:latest
kubectl expose deployment financial-ml --port=8050 --type=LoadBalancer

# View status
kubectl get pods
kubectl get services
```

## 📊 Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test class
python -m pytest tests/test_analytics.py::TestGreeks -v

# Run with coverage
pip install pytest-cov
python -m pytest --cov=src tests/
```

### Linting & Code Quality

```bash
# Install dev tools
pip install flake8 black isort

# Format code
black src/ tests/ examples/

# Check linting
flake8 src/ tests/ examples/

# Sort imports
isort src/ tests/ examples/
```

### Adding Dependencies

```bash
pip install <package>
pip freeze > requirements.txt
```

## 📈 Performance & Scaling

### Caching Strategy
- **Market data**: 5-minute TTL by default (configurable)
- **Option chains**: Per-ticker cache with expiry-based invalidation
- **Probability simulations**: Cached if same ticker/strike/expiry

### Scaling Recommendations
- **Small scale** (<10 tickers): Single container, local cache
- **Medium scale** (10-100 tickers): Docker swarm, Redis cache
- **Large scale** (100+ tickers): Kubernetes, distributed cache, separate compute

## ⚠️ Troubleshooting

**Q: "No data available for ticker"**
- Ticker may be invalid or delisted
- Yahoo Finance may rate-limit; wait a moment and retry
- Check internet connectivity

**Q: "Cache hit" appears repeatedly**
- Expected with 5-minute TTL caching
- To disable: remove `@cached` decorators from `src/data/`

**Q: Docker build fails**
- Ensure Docker & Docker Compose are installed
- Try: `docker-compose build --no-cache`

**Q: Slack alerts not sending**
- Verify `SLACK_WEBHOOK_URL` is set and valid
- Check webhook permissions in Slack

**Q: MLflow not tracking**
- Install MLflow: `pip install mlflow`
- Check MLflow server is running (if using remote)

## 📚 Resources

- [Dash Documentation](https://dash.plotly.com)
- [Black-Scholes Model](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model)
- [Slack API](https://api.slack.com)
- [MLflow Docs](https://mlflow.org)
- [Docker Docs](https://docs.docker.com)

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Open an issue or PR.

## 📞 Support

For questions or issues, open an issue on GitHub.


- **📊 Real-Time Data:** Fetch stock prices and option chains from Yahoo Finance
- **🎯 Advanced Analytics:**
  - Black-Scholes Greeks (delta, gamma, theta, vega, rho)
  - Historical-simulation probability estimates using bootstrap methods
  - Volatility classification (LOW/MEDIUM/HIGH) via KMeans clustering
  - Composite scoring based on weighted greeks and probability
- **📈 Smart Trade Recommendations:** Automated trade levels (buy, stop-loss, target)
- **🔍 Search & Filter:** Real-time search across tickers, strikes, and types
- **⭐ Probability Sorting:** Options automatically sorted by probability of profit
- **🛡️ Production-Ready:**
  - Input validation and defensive error handling
  - Request caching (5-minute TTL) and exponential backoff retries
  - Comprehensive unit tests
  - Docker containerization

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- pip or conda

### 1. Clone & Install

```bash
git clone <repo-url>
cd financial-ml
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
python app.py
```

Open your browser to **http://localhost:8050**

### 3. Run Tests

```bash
python -m pytest -v
```

## Docker Setup

### Build & Run

```bash
docker-compose up --build
```

The dashboard will be available at **http://localhost:8050**

### Rebuild Image

```bash
docker-compose up --build --remove-orphans
```

### Stop

```bash
docker-compose down
```

## Architecture

```
financial-ml/
├── app.py                    # Dash entry point
├── config.py                 # Configuration & weights
├── requirements.txt          # Dependencies
├── Dockerfile                # Container image
├── docker-compose.yml        # Local dev setup
├── src/
│   ├── analytics/            # Core analytics
│   │   ├── probability_model.py      # Greeks & probability simulation
│   │   ├── scoring_model.py          # Composite option scoring
│   │   ├── trade_model.py            # Trade level computation
│   │   └── volatility_model.py       # Vol classification
│   ├── data/                 # Market data
│   │   ├── stocks.py                 # Stock snapshot & price history
│   │   └── options.py                # Option chain fetching
│   ├── dashboard/            # UI & interactions
│   │   ├── layout.py                 # Beautiful responsive layout
│   │   └── callbacks.py              # Dash callbacks with search/sort
│   └── utils/
│       └── cache.py                  # Caching & retry decorators
└── tests/
    └── test_analytics.py     # Comprehensive unit tests
```

## Configuration

Edit `config.py` to customize:

```python
SCORE_WEIGHTS = {
    "delta": 0.25,      # Delta (directional exposure)
    "gamma": 0.10,      # Gamma (acceleration/curvature)
    "theta": 0.15,      # Theta (time decay)
    "vega": 0.20,       # Vega (volatility sensitivity)
    "rho": 0.05,        # Rho (interest rate)
    "volume": 0.10,     # Volume (liquidity)
    "probability": 0.15 # Probability of profit
}

REFRESH_INTERVAL_MS = 30_000  # Auto-refresh every 30 seconds
```

## API & Data

### Stock Data

```python
from src.data.stocks import get_stock_snapshot, get_price_history

# Get snapshot: price & realized volatility
stocks = get_stock_snapshot(["AAPL", "NVDA"])

# Get historical prices
prices = get_price_history("AAPL", period="1y")
```

### Option Chain Data

```python
from src.data.options import get_available_option_expiries, get_options_snapshot

# Get available expirations
expiries = get_available_option_expiries("AAPL")

# Get option chain snapshot
options = get_options_snapshot(["AAPL"], expiries)
```

### Analytics

```python
from src.analytics.probability_model import probability_from_price_series, compute_greeks

# Estimate probability using historical prices
prob = probability_from_price_series(
    price_series=prices,
    strike=175.0,
    option_type="CALL",
    days_to_expiry=30,
    n_sims=2000
)

# Compute Black-Scholes Greeks
greeks = compute_greeks(
    S=175.0,          # Current stock price
    K=180.0,          # Strike price
    T=30/365,         # Time to expiry (fraction of year)
    r=0.05,           # Risk-free rate
    sigma=0.25,       # Volatility
    option_type="call"
)
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest -v

# Run specific test class
python -m pytest tests/test_analytics.py::TestGreeks -v

# Run with coverage
pip install pytest-cov
python -m pytest --cov=src tests/
```

### Linting & Code Quality

```bash
# Install dev dependencies
pip install flake8 black isort

# Format code
black src/ tests/

# Check linting
flake8 src/ tests/
```

### Adding Dependencies

```bash
pip install <package>
pip freeze > requirements.txt
```

## Real-World Enhancements

1. **Production Data Feeds:** Replace yfinance with Polygon, IEX, Tradier, or ORATS for:
   - Lower latency & higher reliability
   - Pre-computed IV surfaces & implied moves
   - Commercial-grade historical data

2. **Backtesting:** Add backtesting module to validate scoring rules:
   ```python
   from src.analytics.backtest import backtest_strategy
   results = backtest_strategy(historical_data, strategy_config)
   ```

3. **Execution:** Integrate with broker APIs (Alpaca, Interactive Brokers, Tradier):
   ```python
   broker.submit_order(symbol, quantity, order_type, price)
   ```

4. **Alerts:** Add Slack/Email/SMS notifications for trade signals

5. **Model Tracking:** Use MLflow or Weights & Biases for experiment tracking

6. **Deployment:** Push to AWS, GCP, or Heroku using Docker

## Logging & Monitoring

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs:

```bash
docker-compose logs -f dashboard
```

## Troubleshooting

**Q: "No data available for ticker"**
- Ticker may be invalid or delisted
- Yahoo Finance may rate-limit; wait a moment and retry

**Q: "Cache hit" appears repeatedly**
- This is expected with 5-minute TTL caching
- To disable: remove `@cached` decorators from `src/data/`

**Q: Docker build fails**
- Ensure Docker & Docker Compose are installed
- Try: `docker-compose build --no-cache`

## License

MIT

## Contact

For questions or contributions, open an issue on GitHub.
