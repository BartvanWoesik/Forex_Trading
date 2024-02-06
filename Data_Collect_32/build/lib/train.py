import mlflow
import joblib
from hydra import compose, initialize
from hydra.utils import instantiate
import pandas as pd
from ProcessData.dataset import Dataset
from ProcessData.data_splitter import data_splitter
from Evaluate.pips import get_pips_margin
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import PrecisionRecallDisplay
from matplotlib import pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.utils import estimator_html_repr
from sklearn.metrics import brier_score_loss

from Model.SklearnPipeline import CustomPipeline

from my_logger.custom_logger import  logger

mlflow.set_tracking_uri('http://127.0.0.1:5000/')


ARTIFACT_PATH = 'artifacts/'


def main():
    initialize(config_path="../conf/", version_base=None)
    cfg = compose(config_name="config.yaml")
    with mlflow.start_run(experiment_id="854451128264867666", run_name="test") as _run:
        # Define data pipeline
        data_pipeline = instantiate(cfg.data_pipeline)
        df = pd.read_csv(cfg.Data_Source)
        df = data_pipeline.apply(df.copy())
        # Create Dasaset
        dataset = Dataset(data=df, data_splitter=data_splitter)

        # Define Indicators
        model_features = ['rsi' ,'mfi', 'tv', 'sma', 'williams', 'regrs', 'cci', 'close_price', 'open_price']

        # Create model 
        logger.info('Create model')
        clf = HistGradientBoostingClassifier(**cfg.model.model_params)
        model = CustomPipeline(indicators = model_features, window =  cfg.model.feature_depth)
    
        # Calibrate classifier
        calibrated_clf = CalibratedClassifierCV(clf, method = "isotonic", cv=10, ensemble=False)
        # Add calibration to the pipeline
        model.pipeline.steps.append(('calibrated_classifier', calibrated_clf))
        # Fit model
        model = model.fit(
            dataset.X_train,
            dataset.y_train,
            sample_weight=dataset.X_train["sample_weight"],
        )



        for split_name, (X, y) in dataset.splits.items():
            mlflow.log_metric(
                f"Pips-{split_name}",
                get_pips_margin(
                    model.predict_proba(X).T[1],
                    X["next_close_price1"],
                    X["close_price1"],
                    threshold=0.7
                ),
            )

       

        pr_path = 'Precision-Recall/'
        for split_name, (X, y) in dataset.splits.items():

            # Create Precision-Recall curve
            display = PrecisionRecallDisplay.from_estimator(
                model.pipeline, X, y,  plot_chance_level=True
            )
            _ = display.ax_.set_title(f"2-class Precision-Recall curve - {split_name}")
            plt.savefig(ARTIFACT_PATH + pr_path +f'pr-{split_name}.jpeg')
            mlflow.log_artifact(ARTIFACT_PATH + pr_path +f'pr-{split_name}.jpeg', artifact_path=pr_path[:-1])
        mlflow.log_artifact("src\scikit_learn_pipeline.html", artifact_path='pipeline')



        for split_name, (X, y) in dataset.splits.items():
            mlflow.log_metric(f"Brier-{split_name}", brier_score_loss(y, model.predict_proba(X).T[1]))
        mlflow.sklearn.log_model(model, 'model')
        
        mlflow.log_param(
            "OOT_date", min(pd.to_datetime(dataset.X_oot["Datum"], dayfirst=True))
        )
    

        joblib.dump(model, "model.pkl")

        mlflow.log_artifact("conf\config.yaml")
        mlflow.log_params(cfg.model.model_params)
        mlflow.log_param("feature_depth", cfg.model.feature_depth)


if __name__ == "__main__":
    main()
