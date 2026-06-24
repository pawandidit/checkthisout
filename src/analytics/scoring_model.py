import sys
from pathlib import Path

# Ensure config can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import SCORE_WEIGHTS

def normalize(s):
    return s / s.max() if s.max() > 0 else s

def score_options(df):
    for col in ["delta", "gamma", "theta", "vega", "rho", "volume", "probability"]:
        df[f"norm_{col}"] = normalize(df[col])

    df["score"] = sum(
        SCORE_WEIGHTS[c] * df[f"norm_{c}"]
        for c in SCORE_WEIGHTS
    ) * 100

    return df
