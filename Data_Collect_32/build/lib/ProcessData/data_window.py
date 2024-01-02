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






def add_normalized_cols(df: pd.DataFrame, cols: list[str], window: int = 10) -> pd.DataFrame:
    norm_col_names = []
    for _,col in enumerate(cols):
        cols_names = [col+str(i) for i in range(1,window+1)]
        norm_col_names = [col+ '_norm_' +str(i) for i in range(1,window+1)]
        ranges = np.apply_along_axis(min_max_norm, axis = 1 , arr = df[cols_names])
        df_ranges = pd.DataFrame(ranges, columns =  norm_col_names)

        df = pd.concat([df, df_ranges], axis = 1)
      
    return df





