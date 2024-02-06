import numpy as np
import pandas as pd
from my_logger.custom_logger import logger

from sklearn.base import BaseEstimator, TransformerMixin


class AddNormalizedColsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, indicators: list[str], window: int):
        self.indicators = indicators
        self.window = window
        

    def fit(self,  *args, **kwargs):
        return self

    def transform(self, X: pd.DataFrame, *args):
        df = X.copy()
        for col in self.indicators:
                
                # Create col names
                cols_names = [col + str(i) for i in range(1, self.window + 1)]
                logger.info(f'Normalizing cols: {cols_names}')
                ranges = np.apply_along_axis(self.min_max_norm, axis=1, arr=df[cols_names])
                assert ranges.shape[0] == df.shape[0]
                df_ranges = pd.DataFrame(ranges, columns=cols_names)
                df = df.reset_index(drop = True)
                df[cols_names] = df_ranges[cols_names]
   
        
        return  df
    
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
