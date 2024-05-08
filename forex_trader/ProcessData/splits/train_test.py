from sklearn.model_selection import ShuffleSplit
import pandas as pd

def add_train_test_indixes(
    X: pd.DataFrame, random_state: int = 42, test_size: int = 0.2
) -> pd.DataFrame:
    """
    Adds train and test indexes to the given DataFrame.

    Parameters:
    - X (pd.DataFrame): The input DataFrame.
    - random_state (int): Random seed for reproducibility. Default is 42.
    - test_size (int): Proportion of the data to be used for testing. Default is 0.2.

    Returns:
    - pd.DataFrame: The input DataFrame with train and test indexes added.
    """

    splitter = ShuffleSplit(test_size=test_size, n_splits=1, random_state=random_state)
    split = splitter.split(X)
    train_ind, test_ind = next(split)
    X.loc[train_ind, "train"] = 1
    X.loc[test_ind, "test"] = 1

    return X
