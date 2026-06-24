# Examples directory

This directory contains practical examples of using the financial-ml library.

## Available Examples

1. **01_backtest_example.py** - Backtesting scoring-based options strategies
2. **02_slack_alerts_example.py** - Setting up Slack notifications for trading signals
3. **03_mlflow_tracking_example.py** - Tracking experiments with MLflow
4. **04_data_providers_example.py** - Using pluggable market data providers

## Running Examples

```bash
python examples/01_backtest_example.py
python examples/02_slack_alerts_example.py
python examples/03_mlflow_tracking_example.py
python examples/04_data_providers_example.py
```

## Requirements

- Base requirements: see ../requirements.txt
- MLflow tracking: `pip install mlflow`
- Slack alerts: Set SLACK_WEBHOOK_URL environment variable
