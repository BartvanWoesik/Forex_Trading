from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from .model import AddNormalizedColsTransformer
import pandas as pd
from my_logger.custom_logger import logger
from sklearn.preprocessing import StandardScaler

class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, features: list[str], depth: int) -> None:


        self.features = self.featureconstructer(list(set(features)), depth)


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

    def transform(self, X):
        logger.info('Selecting features from Dataset')
        return X[list(self.features)]

    def fit_transform(self, X, *fit_args, **fit_kwargs):
        return self.transform(X)

    def fit(self, X, *fit_args, **fit_kwargs):
        return self







class CustomPipeline(BaseEstimator, TransformerMixin):
    def __init__(self, indicators, window=10):
        self.features = self.featureconstructer(indicators, window)
        self.indicators = indicators
        self.window = window
        # Create an instance of the FeatureSelector
        feature_selector = FeatureSelector(self.features)

        # Create an instance of the StandardScaler
        self.pipeline = Pipeline(
            [
                ("FeatureSelector", feature_selector),
                ('NormCols', AddNormalizedColsTransformer(self.indicators, self.window)),
              
              
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
        logger.info(f"Features included in the model are:\n{', '.join(features)}")
        return features


    def fit(self, X: pd.DataFrame, y=None, sample_weight=None):
        logger.info("Start fitting the pipeline.")


        self.pipeline.fit(X = X,y = y)


        return self

    def transform(self, X):
        self.pipeline.transform(X = X)

    def predict(self, X):
        # Use predict on the final step
        transformed_data = self.transfrom_without_predictor(X)
        return self.pipeline.steps[-1][1].predict(transformed_data)

    def predict_proba(self, X):
        transformed_data = self.transfrom_without_predictor(X)
        return self.pipeline.steps[-1][1].predict_proba(X = transformed_data)
    

    def transfrom_without_predictor(self, X: pd.DataFrame) -> pd.DataFrame:
        for _, step in self.pipeline.steps[:-1]:
        
            X = step.transform(X)
        return X
 
