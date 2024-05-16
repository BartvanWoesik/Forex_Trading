import pandas as pd
import numpy as np


def get_pips_margin(
    predictions: np.array,
    next_close_price: pd.DataFrame,
    close_price: pd.DataFrame,
    threshold: float =1,
    commision: float = 0.00006
) -> float:
    """
    Find the Pips margins based on predictions and true values.

    Args:
        predictions: Data to make predictions on
        next_close_price: price of market in next bar
        close_price: close price of current bar
        threshold: in case of predict_proba
        commision: cost of transaction

    Returns:
        total_margin: Net amount of pips gained
    """     
    diff = next_close_price - close_price
    realized_positions = diff[predictions >= threshold] - commision
    total_margin = sum(realized_positions.dropna())
    return total_margin * 1000
