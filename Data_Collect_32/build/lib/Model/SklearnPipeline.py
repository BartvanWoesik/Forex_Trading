
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from .model import AddNormalizedColsTransformer
from sklearn.ensemble import HistGradientBoostingClassifier

class CustomPipeline(BaseEstimator, TransformerMixin):
    def __init__(self, cols_to_normalize, window=10):
        self.cols_to_normalize = cols_to_normalize
        self.window = window
        self.pipeline = Pipeline([
            ('add_normalized_cols', AddNormalizedColsTransformer(cols=cols_to_normalize, window=window)),
            ('Model', HistGradientBoostingClassifier())
        ])

    def fit(self, X, y=None):
        transformed_data = self.pipeline.named_steps['add_normalized_cols'].transform(X)
        self.pipeline.named_steps['Model'].fit(transformed_data, y)
        return self

    def transform(self, X):
        return self.pipeline.named_steps['add_normalized_cols'].transform(X)
    
    def predict(self, X):
        # Use predict on the final step
        transformed_data = self.pipeline.named_steps['add_normalized_cols'].transform(X)
        return self.pipeline.named_steps['Model'].predict(transformed_data)
    
    
    def predict_proba(self, X):
        transformed_data = self.pipeline.named_steps['add_normalized_cols'].transform(X)
        return self.pipeline.named_steps['Model'].predict_proba(transformed_data)