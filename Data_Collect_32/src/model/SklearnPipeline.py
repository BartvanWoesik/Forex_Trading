from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from .model import AddNormalizedColsTransformer
import pandas as pd


class featureselector(BaseEstimator, TransformerMixin):
    def __init__(self, features: list[str]) -> None:
        self.features = set(features)

    def transform(self, X):
        return X[list(self.features)]
    
    def fit_transform(self, X, *fit_args):
        return X[list(self.features)]

class CustomPipeline(BaseEstimator, TransformerMixin):
    def __init__(self, indicators, window=10):
        self.features = self.featureconstructer(indicators, window)
        self.indicators = indicators
        self.window = window
        self.pipeline = Pipeline(
            [
                ("feature selector", featureselector(self.features)),
                (
                    "add_normalized_cols",
                    AddNormalizedColsTransformer(self.indicators, self.window),
                ),
              
              
            ]
        )

    def featureconstructer(self, cols: list[str], window: int) -> list[str]:
        """
        Construct list of features that can be extracted from full dataset. 

        Args:
            cols list[str]: List of selected indicators from dataset
            window int: number of bars that need to be looked back
        """
        features = []
        for col in cols:
            for i in range(1,window +1):
                new_feature = col+str(i)
                features.append(new_feature)
        return features


    def fit(self, X: pd.DataFrame, y=None, sample_weight=None):
        # Transform data with all steps except the last one
        transformed_data = self.transfrom_without_predictor(X)

        # Fit the last step with the transformed data
        self.pipeline.steps[-1][1].fit(transformed_data, y, sample_weight)
        return self

    def transform(self, X):
        return self.transfrom_without_predictor(X)

    def predict(self, X):
        # Use predict on the final step
        transformed_data = self.transfrom_without_predictor(X)
        return self.pipeline.steps[-1][1].predict(transformed_data)

    def predict_proba(self, X):
        transformed_data = self.transfrom_without_predictor(X)
        return self.pipeline.steps[-1][1].predict_proba(transformed_data)
    

    def transfrom_without_predictor(self, X: pd.DataFrame) -> pd.DataFrame:
        for _, step in self.pipeline.steps[:-1]:

            transformed_data = step.transform(X)
        return transformed_data
 


