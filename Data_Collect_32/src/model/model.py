import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class AddNormalizedColsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, cols, window=10):
        self.cols = cols
        self.window = window

    def fit(self, X, y=None):
        return self

    def transform(self, X, *args):
        df = X.copy()

        norm_col_names = []
        tot_cols = []
        for col in self.cols:
                # Create col names
                cols_names = [col + str(i) for i in range(1, self.window + 1)]
                norm_col_names = [
                    col + "_norm_" + str(i) for i in range(1, self.window + 1)
                ]

                ranges = np.apply_along_axis(self.min_max_norm, axis=1, arr=df[cols_names])
                assert ranges.shape[0] == df.shape[0]
                df_ranges = pd.DataFrame(ranges, columns=norm_col_names)
                df = pd.concat(
                    [
                        df.reset_index(drop=True),
                        df_ranges[norm_col_names].reset_index(drop=True),
                    ],
                    axis=1,
                )
                tot_cols += norm_col_names
                tot_cols += cols_names
        return df[tot_cols]
    
    def fit_transform(self,X, *fit_args):
        return self.transform(X)

    def min_max_norm(self, row):
        _min = row.min()
        if _min == 0:
            _min += 0.00001
        _max = row.max()
        if _max == 0:
            _max += 0.00001
        return (row - _min) / (_max / _min)
