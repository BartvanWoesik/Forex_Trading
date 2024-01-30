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

PATH = "./data/Data_collect_32.csv"


def main():
    initialize(config_path="../conf/")
    cfg = compose(config_name="config.yaml")
    with mlflow.start_run(experiment_id="854451128264867666", run_name="test") as _run:
        # Define pipeline
        pipeline = instantiate(cfg.data_pipeline)
        df = pd.read_csv(cfg.Data_Source)
        df = pipeline.apply(df.copy())
        model_features = ['rsi', 'mfi', 'tv', 'sma', 'williams', 'regrs', 'cci']
        dataset = Dataset(data=df, data_splitter=data_splitter)
        clf = HistGradientBoostingClassifier(**cfg.model.model_params)
        custompipeline = CustomPipeline(indicators = model_features, window =  10)
        custompipeline.pipeline.steps.append(("final model", clf))
        print(dataset.X_train.columns)
        model = custompipeline.fit(
            dataset.X_train,
            dataset.y_train,
            sample_weight=dataset.X_train["sample_weight"],
        )
        pred_oot = model.predict(dataset.X_oot)
        mlflow.log_metric(
            "Pips",
            get_pips_margin(
                pred_oot,
                dataset.X_oot["next_close_price"],
                dataset.X_oot["close_price"],
            ),
        )

        calibrated_clf = CalibratedClassifierCV(clf, cv="prefit")
        procceced_data_train = custompipeline.transform(dataset.X_train)
        procceced_data_oot = custompipeline.transform(dataset.X_oot)
        procceced_data_test = custompipeline.transform(dataset.X_test)
        calibrated_clf.fit(procceced_data_train, dataset.y_train)
        pred_calibrated = calibrated_clf.predict_proba(procceced_data_oot).T[1]
        threshold = max(
            calibration_curve(
                dataset.y_test, calibrated_clf.predict_proba(procceced_data_test).T[1]
            )[1]
        )
        mlflow.log_metric(
            "Pips calibrated",
            get_pips_margin(
                pred_calibrated,
                dataset.X_oot["next_close_price"],
                dataset.X_oot["close_price"],
                threshold=threshold,
            ),
        )


        mlflow.sklearn.log_model(custompipeline, 'model')
        
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
