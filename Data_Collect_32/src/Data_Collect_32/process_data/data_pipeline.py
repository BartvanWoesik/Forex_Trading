from dataclasses import dataclass
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from copy import deepcopy
import logging

import pickle as pkl
import numpy as np

from typing import Optional
                

def safe(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        cp_args = deepcopy(args)
        cp_kwargs = deepcopy(kwargs)
        res = fn(self, *cp_args, **cp_kwargs)
        return res
    return wrapper

class PandasDataPipeline:

    def __init__(
        self,
        steps,
        name: str = 'pipeline',
        cache: bool = False,
    ) -> None:
        self.steps = steps
        self.name = name
        self.cache = cache

    # @staticmethod
    # def _get_step_name(step) -> str:
    #     if isinstance(step, tuple):    

    def _apply(self, df: pd.DataFrame, verbose: Optional[bool]= True) -> pd.DataFrame:

        for step_number, step in enumerate(self.steps, start=1):
            if isinstance(step,tuple):
                df = step[1](df)
            else:
                df = step(df)
        return df

    @safe
    def apply(self, df: pd.DataFrame, verbose: Optional[bool] = True)  -> pd.DataFrame:
        return self._apply(df, verbose=verbose)
    