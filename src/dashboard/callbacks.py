from dash import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import logging

from src.data.stocks import get_stock_snapshot, get_price_history
from src.data.options import get_available_option_expiries, get_options_snapshot
from src.analytics.volatility_model import classify_volatility
from src.analytics.probability_model import probability_from_price_series
from src.analytics.scoring_model import score_options
from src.analytics.trade_model import compute_trade_levels, assign_strategy

logger = logging.getLogger(__name__)


def register_callbacks(app):

    @app.callback(
        Output("ticker-selector", "options"),
        Input("ticker-input", "value")
    )
    def add_ticker(t):
        if not t:
            return []
        t = t.upper()
        # basic validation: avoid invalid or too-long inputs
        if not isinstance(t, str) or len(t) > 8:
            return []
        return [{"label": t, "value": t}]

    @app.callback(
        Output("expiry-selector", "options"),
        Input("ticker-selector", "value")
    )
    def update_expiries(tickers):
        if not tickers:
            return []

        expiries = set()
        for t in tickers:
            try:
                expiries.update(get_available_option_expiries(t))
            except Exception as e:
                logger.warning(f"Failed to fetch expiries for {t}: {e}")

        return [{"label": e, "value": e} for e in sorted(expiries)]

    @app.callback(
        Output("dashboard-content", "children"),
        Input("refresh", "n_intervals"),
        Input("ticker-selector", "value"),
        Input("expiry-selector", "value"),
        Input("options-search", "value"),
        Input("sort-by", "value")
    )
    def update_dashboard(_, tickers, expiries, search_term, sort_by):
        if not tickers or not expiries:
            return dbc.Alert("Select ticker(s) and expiry date(s) to begin", color="info", className="mt-3")

        if len(tickers) > 5:
            return dbc.Alert("Select up to 5 tickers to avoid heavy queries", color="warning", className="mt-3")

        try:
            # Fetch stocks
            stocks = get_stock_snapshot(tickers)
            if stocks.empty:
                return dbc.Alert("No stock data available for selected tickers", color="warning", className="mt-3")

            stocks["vol_regime"] = classify_volatility(stocks["realized_vol"])
            stocks["strategy"] = stocks["vol_regime"].apply(assign_strategy)

            # Fetch options
            options = get_options_snapshot(tickers, expiries)
            if options.empty:
                return dbc.Alert("No options data available for selected tickers/expiries", color="warning", className="mt-3")

            # Fetch price history per ticker
            price_hist = {t: get_price_history(t, period="1y") for t in tickers}

            # Compute probabilities using historical data
            options["probability"] = options.apply(
                lambda r: probability_from_price_series(
                    price_hist.get(r["ticker"], []),
                    r["strike"],
                    r["type"],
                    days_to_expiry=30
                ),
                axis=1
            )

            # Score options
            options = score_options(options)

            # Apply search filter
            if search_term and isinstance(search_term, str):
                search_term_lower = search_term.lower()
                options = options[
                    options["ticker"].str.lower().str.contains(search_term_lower, na=False) |
                    options["type"].str.lower().str.contains(search_term_lower, na=False) |
                    options["strike"].astype(str).str.contains(search_term_lower, na=False)
                ]

            # Apply sorting
            if sort_by == "probability_desc":
                options = options.sort_values("probability", ascending=False)
            elif sort_by == "score_desc":
                options = options.sort_values("score", ascending=False)
            elif sort_by == "strike_asc":
                options = options.sort_values("strike", ascending=True)
            elif sort_by == "expiry_asc":
                options = options.sort_values("expiry", ascending=True)

            # Compute trades
            trades = compute_trade_levels(stocks, options)

            # Build display tables
            stocks_table = _build_stocks_table(trades["stocks"])
            options_table = _build_options_table(trades["options"])

            return [stocks_table, html.Hr(), options_table]

        except Exception as e:
            logger.exception(f"Dashboard error: {e}")
            return dbc.Alert(f"An error occurred: {str(e)}", color="danger", className="mt-3")


def _build_stocks_table(stocks_df):
    """Build a styled Bootstrap table for stocks."""
    if stocks_df.empty:
        return dbc.Alert("No stocks to display", color="info")

    # Format numeric columns
    stocks_df = stocks_df.copy()
    stocks_df["price"] = stocks_df["price"].apply(lambda x: f"${x:.2f}")
    stocks_df["realized_vol"] = stocks_df["realized_vol"].apply(lambda x: f"{x*100:.2f}%")

    # Rename columns for display
    display_df = stocks_df[["ticker", "price", "realized_vol", "vol_regime", "strategy"]].copy()
    display_df.columns = ["Ticker", "Price", "Volatility", "Vol Regime", "Strategy"]

    return dbc.Card([
        dbc.CardHeader(html.H5("📈 Stock Overview", className="mb-0 fw-bold")),
        dbc.CardBody([
            dbc.Table.from_dataframe(
                display_df,
                striped=True,
                bordered=True,
                hover=True,
                responsive="sm",
                className="mb-0"
            )
        ])
    ], className="mb-4")


def _build_options_table(options_df):
    """Build a styled Bootstrap table for options with color coding."""
    if options_df.empty:
        return dbc.Alert("No options to display", color="info")

    options_df = options_df.copy()

    # Format numeric columns
    options_df["price"] = options_df["price"].apply(lambda x: f"${x:.2f}")
    options_df["strike"] = options_df["strike"].apply(lambda x: f"${x:.0f}")
    options_df["probability"] = options_df["probability"].apply(lambda x: f"{x:.1f}%")
    options_df["score"] = options_df["score"].apply(lambda x: f"{x:.1f}")

    # Rename columns
    display_df = options_df[
        ["ticker", "type", "strike", "price", "expiry", "probability", "delta", "gamma", "theta", "vega", "score"]
    ].copy()
    display_df.columns = [
        "Ticker", "Type", "Strike", "Price", "Expiry", "Probability ⭐", "Delta", "Gamma", "Theta", "Vega", "Score"
    ]

    # Create table cells with color coding for probability
    rows = []
    for idx, row in display_df.iterrows():
        prob_str = row["Probability ⭐"]
        # Extract numeric value for color coding
        prob_val = float(prob_str.rstrip('%'))

        # Color code: green if prob > 60, yellow if 40-60, red if < 40
        if prob_val > 60:
            prob_bg = "success"
            prob_text = "light"
        elif prob_val > 40:
            prob_bg = "warning"
            prob_text = "dark"
        else:
            prob_bg = "danger"
            prob_text = "light"

        cells = [
            html.Td(row[col]) for col in display_df.columns[:-1]
        ]
        cells.insert(-1, html.Td(
            dbc.Badge(prob_str, color=prob_bg, text_color=prob_text, pill=True),
            className="text-center"
        ))
        rows.append(html.Tr(cells))

    header = html.Thead(html.Tr([html.Th(col) for col in display_df.columns]))
    body = html.Tbody(rows)

    return dbc.Card([
        dbc.CardHeader(html.H5("🎯 Options Analysis", className="mb-0 fw-bold")),
        dbc.CardBody([
            html.Div(
                html.Table([header, body], className="table table-striped table-bordered table-hover table-sm mb-0"),
                style={"overflowX": "auto"}
            )
        ])
    ])
