from dash import dcc, html
import dash_bootstrap_components as dbc
from config import REFRESH_INTERVAL_MS

def get_layout():
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("📊 Options Intelligence Dashboard", className="mb-1 mt-4 fw-bold text-primary"),
                html.P("Real-time probability analysis, volatility classification, and trade recommendations",
                       className="text-muted small mb-4")
            ])
        ]),

        # Control Panel
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Ticker Search & Selection", className="fw-bold"),
                        dcc.Input(
                            id="ticker-input",
                            placeholder="Enter ticker (e.g., NVDA, AAPL)",
                            type="text",
                            className="form-control mb-2",
                            maxLength=8
                        ),
                        dcc.Dropdown(
                            id="ticker-selector",
                            multi=True,
                            placeholder="Selected tickers will appear here...",
                            className="mb-2"
                        ),
                        html.Small("Max 5 tickers. Type to search.", className="text-muted")
                    ], md=6),
                    dbc.Col([
                        html.Label("Expiration Dates", className="fw-bold"),
                        dcc.Dropdown(
                            id="expiry-selector",
                            multi=True,
                            placeholder="Select expiry dates...",
                            className="mb-2"
                        ),
                        html.Small("Expiries will auto-populate based on selected tickers.", className="text-muted")
                    ], md=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Label("Search Options & Sort", className="fw-bold mt-3"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="options-search",
                                placeholder="Search by ticker, strike, type...",
                                type="text",
                                className="form-control"
                            ),
                            dcc.Dropdown(
                                id="sort-by",
                                options=[
                                    {"label": "💯 Probability (High→Low)", "value": "probability_desc"},
                                    {"label": "💰 Score (High→Low)", "value": "score_desc"},
                                    {"label": "🎯 Strike Price (Low→High)", "value": "strike_asc"},
                                    {"label": "⏱️ Time to Expiry", "value": "expiry_asc"},
                                ],
                                value="probability_desc",
                                className="mb-0",
                                clearable=False
                            )
                        ])
                    ], md=12)
                ])
            ])
        ], className="mb-4"),

        # Hidden interval for auto-refresh
        dcc.Interval(id="refresh", interval=REFRESH_INTERVAL_MS),

        # Loading indicator
        dcc.Loading(id="loading", type="default", children=[
            html.Div(id="dashboard-content", className="mt-4")
        ])
    ], fluid=True, className="py-3")
