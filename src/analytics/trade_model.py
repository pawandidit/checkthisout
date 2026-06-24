def assign_strategy(vol_regime):
    return {
        "LOW": "Long Call / Put",
        "MEDIUM": "Debit Spread",
        "HIGH": "Credit Spread"
    }.get(vol_regime, "Neutral")

def compute_trade_levels(stocks, options):
    options = options.sort_values("score", ascending=False).head(20)

    options["buy"] = options["price"]
    options["stop_loss"] = options["price"] * 0.7
    options["target"] = options["price"] * 1.6

    return {
        "stocks": stocks,
        "options": options
    }
