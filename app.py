import logging
from dash import Dash
import dash_bootstrap_components as dbc

from src.dashboard.layout import get_layout
from src.dashboard.callbacks import register_callbacks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set title and layout
app.title = "Options Intelligence Dashboard"
app.layout = get_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
