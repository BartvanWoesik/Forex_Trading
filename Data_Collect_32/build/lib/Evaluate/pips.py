import pandas as pd


def get_pips_margin(
    predictions,
    next_close_price: pd.DataFrame,
    close_price: pd.DataFrame,
    threshold=1,
    commision: float = 0.00006,
) -> float:
    """
    predictions: Data to make predictions on
    next_close_price: price of market in next bar
    close_price: close price of current bar
    commision: cost of transaction
    """

    diff = next_close_price - close_price
    realized_positions = diff[predictions >= threshold] - commision
    total_margin = sum(realized_positions)
    return total_margin * 1000
