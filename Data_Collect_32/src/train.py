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

from sklearn.calibration import calibration_curve
from sklearn.utils import estimator_html_repr
from sklearn.metrics import brier_score_loss

from Model.SklearnPipeline import CustomPipeline

from my_logger.custom_logger import  logger

mlflow.set_tracking_uri('http://127.0.0.1:5000/')





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
        model_features = ['rsi', 'mfi', 'tv', 'sma', 'williams', 'regrs', 'cci', 'close_price', 'open_price']

        # Create model 
        logger.info('Create model')
        clf = HistGradientBoostingClassifier(**cfg.model.model_params)
        model = CustomPipeline(indicators = model_features, window =  cfg.model.feature_depth)
        model.pipeline.steps.append(("final model", clf))

        # Fit model
        model = model.fit(
            dataset.X_train,
            dataset.y_train,
            sample_weight=dataset.X_train["sample_weight"],
        )
        pred_oot = model.predict(dataset.X_oot)
        mlflow.log_metric(
            "Pips",
            get_pips_margin(
                pred_oot,
                dataset.X_oot["next_close_price1"],
                dataset.X_oot["close_price1"],
            ),
        )

        # Calibrate classifier
        calibrated_clf = CalibratedClassifierCV(model.pipeline.steps[-1][1], cv="prefit")

        # TransformData
        procceced_data_train = model.transfrom_without_predictor(dataset.X_train)
        procceced_data_oot = model.transfrom_without_predictor(dataset.X_oot)
        procceced_data_test = model.transfrom_without_predictor(dataset.X_test)

        # Fit Calibrate classifier
        calibrated_clf.fit(procceced_data_train, dataset.y_train)
        pred_calibrated = calibrated_clf.predict_proba(procceced_data_oot).T[1]

        # Log Metrics
        threshold = max(
            calibration_curve(
                dataset.y_test, calibrated_clf.predict_proba(procceced_data_test).T[1]
            )[1]
        )
        mlflow.log_metric(
            "Pips calibrated",
            get_pips_margin(
                pred_calibrated,
                dataset.X_oot["next_close_price1"],
                dataset.X_oot["close_price1"],
                threshold=threshold,
            ),
        )


        mlflow.sklearn.log_model(model, 'model')
        
        mlflow.log_metric("Threshold", threshold)
        mlflow.log_param(
            "OOT_date", min(pd.to_datetime(dataset.X_oot["Datum"], dayfirst=True))
        )
    

        mlflow.log_metric("brier", brier_score_loss(dataset.y_test, calibrated_clf.predict_proba(procceced_data_test).T[1]))
        joblib.dump(model, "model.pkl")

        mlflow.log_artifact("conf\config.yaml")
        mlflow.log_params(cfg.model.model_params)
        mlflow.log_param("feature_depth", cfg.model.feature_depth)


if __name__ == "__main__":
    main()
