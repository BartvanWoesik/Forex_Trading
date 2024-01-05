from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from .model import AddNormalizedColsTransformer


class CustomPipeline(BaseEstimator, TransformerMixin):
    def __init__(self, cols_to_normalize, window=10):
        self.cols_to_normalize = cols_to_normalize
        self.window = window
        self.pipeline = Pipeline(
            [
                ("feature selector", featureselector(self.cols_to_normalize)),
                (
                    "add_normalized_cols",
                    AddNormalizedColsTransformer(cols=cols_to_normalize, window=window),
                ),
            ]
        )

    def fit(self, X, y=None, sample_weight=None):
        transformed_data = self.pipeline.named_steps["add_normalized_cols"].transform(X)
        self.pipeline.named_steps["final model"].fit(transformed_data, y, sample_weight)
        return self

    def transform(self, X):
        return self.pipeline.named_steps["add_normalized_cols"].transform(X)

    def predict(self, X):
        # Use predict on the final step
        transformed_data = self.pipeline.named_steps["add_normalized_cols"].transform(X)
        return self.pipeline.named_steps["final model"].predict(transformed_data)

    def predict_proba(self, X):
        transformed_data = self.pipeline.named_steps["add_normalized_cols"].transform(X)
        return self.pipeline.named_steps["final model"].predict_proba(transformed_data)


class featureselector:
    def __init__(self, features: list[str]) -> None:
        self.features = features

    def transforom(self, X):
        return X[self.features]
