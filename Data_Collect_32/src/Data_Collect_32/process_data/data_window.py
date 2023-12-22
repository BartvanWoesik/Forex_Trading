import numpy as np
import pandas as pd

def min_max_norm(row: np.array) -> np.array:
        _min = row.min()
        if _min == 0:
             _min += 0.00001
        _max = row.max()
        if _max == 0:
            _max += 0.00001
        return (row - _min) / (_max / _min)

def shift_column(col: pd.Series, window: int = 10) -> pd.Series:
    ranges = np.array([ col.shift(i) for i in range(0,window+1)]).T
    return ranges

def normalize_column(col: pd.Series, window: int = 10) -> pd.Series:
    ranges = np.array([ col.shift(i) for i in range(0,window+1)]).T
    return np.apply_along_axis(min_max_norm, axis = 1, arr = ranges)


def add_normalized_cols(df: pd.DataFrame, cols: list[str], window: int = 10) -> pd.DataFrame:
    norm_col_names = []
    for i,col in enumerate(cols):

        norm_col_names = [col+ '_norm_' +str(i) for i in range(0,window+1)]
        ranges = normalize_column(df[col], window)
        df_ranges = pd.DataFrame(ranges, columns =  norm_col_names)
        df = pd.merge(df, df_ranges, left_index = True, right_index=True)
    return df

def add_time_cols(df: pd.DataFrame, cols: list[str], window: int = 10) -> pd.DataFrame:
    col_names = []
    for i,col in enumerate(cols):

        col_names = [col +'_'+ str(i) for i in range(0,window+1)]
        ranges = shift_column(df[col], window)
        df_ranges = pd.DataFrame(ranges, columns =  col_names)
        df = pd.merge(df, df_ranges, left_index = True, right_index=True)
    return df




