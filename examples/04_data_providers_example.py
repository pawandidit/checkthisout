"""
Example: Using Different Market Data Providers

This script demonstrates how to use the pluggable data provider interface
to swap between different market data sources.

Supported providers:
- yfinance (default) - Free, good for prototyping
- polygon - Lower latency, better data quality
- iex - Good for institutional use
- tradier - Full options data, execution ready
- orats - Best for options-specific analysis

To add a new provider, inherit from MarketDataProvider in src/data/providers.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from src.data.providers import get_data_provider


def main():
    """Run data provider example."""
    print("=" * 60)
    print("Market Data Providers Example")
    print("=" * 60)

    # Use default provider (yfinance)
    print("\n1. Using YFinance Provider (default)...")
    try:
        provider = get_data_provider("yfinance")
        
        ticker = "AAPL"
        print(f"\n   Fetching data for {ticker}...")
        
        # Get current price
        price = provider.get_stock_price(ticker)
        print(f"   Current Price: ${price:.2f}")
        
        # Get price history
        history = provider.get_price_history(ticker, period="3mo")
        print(f"   3-Month History: {len(history)} data points")
        print(f"   Price Range: ${history.min():.2f} - ${history.max():.2f}")
        
        # Get option expiries
        expiries = provider.get_option_expiries(ticker)
        print(f"   Available Expiries: {expiries[:3]} ...")
        
        # Get option chain
        if expiries:
            chain = provider.get_option_chain(ticker, expiries[0])
            calls = chain.get("calls", [])
            puts = chain.get("puts", [])
            print(f"   {expiries[0]} Calls: {len(calls) if hasattr(calls, '__len__') else 'N/A'}")
            print(f"   {expiries[0]} Puts: {len(puts) if hasattr(puts, '__len__') else 'N/A'}")
    
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 60)
    print("Provider Examples Demonstration Complete")
    print("\nTo add a custom provider (e.g., Polygon, IEX):")
    print("  1. Inherit from MarketDataProvider")
    print("  2. Implement all abstract methods")
    print("  3. Register in get_data_provider() factory")
    print("  4. Update DATA_PROVIDER env var to use it")
    print("=" * 60)


if __name__ == "__main__":
    main()
