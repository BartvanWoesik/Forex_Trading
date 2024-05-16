import mlflow
import pickle
import os
from hydra import compose, initialize
from hydra.utils import instantiate
import pandas as pd
from matplotlib import pyplot as plt

from sklearn.metrics import PrecisionRecallDisplay
from sklearn.metrics import brier_score_loss

from model_forge.data.dataset import Dataset
from model_forge.model.model_orchastrator import ModelOrchestrator

from forex_trader.ProcessData.data_splitter import data_splitter
from forex_trader.Evaluate.pips import get_pips_margin

from my_logger.custom_logger import  logger

from forex_trader.Evaluate.density import plot_density

mlflow.set_tracking_uri('http://127.0.0.1:5000/')


ARTIFACT_PATH = 'artifacts/'


def main():
    initialize(config_path="conf/", version_base=None)
    cfg = compose(config_name="config.yaml")
    with mlflow.start_run(experiment_id="854451128264867666", run_name="test") as _run:
        # Define data pipeline
        data_pipeline = instantiate(cfg.data_pipeline)
        df = pd.read_csv(cfg.Data_Source)
        df = data_pipeline.apply(df.copy())
        logger.info(f"Data shape: {df.shape}")
        # Create Dasaset
        dataset = Dataset(data=df, splits_columns=['train', 'test'])


        # Create model 
        logger.info('Create model')
        model_orchestrator = ModelOrchestrator(cfg)
        model = model_orchestrator.create_pipeline()
    
        # Calibrate classifier
        # calibrated_clf = CalibratedClassifierCV(clf,  cv=10, ensemble=False)
        # Add calibration to the pipeline
        # model.pipeline.steps.append(('calibrated_classifier', calibrated_clf))
        # Fit model
        model = model.fit(
            dataset.X_train,
            dataset.y_train,
            # sample_weight=dataset.X_train["sample_weight"],
        )


        



            
    
        pr_path = 'Precision-Recall/'
        dens_path = 'Density/'
        for split_name, (X, y) in dataset:

            predproba = model.predict_proba(X)
            mlflow.log_metric(
                f"Pips-{split_name}",
                get_pips_margin(
                    predproba,
                    X["next_close_price1"],
                    X["close_price1"],
                    threshold=0.55
                ),
            )
            # Create Precision-Recall curve
            display = PrecisionRecallDisplay.from_predictions(
                 y, predproba,  plot_chance_level=True
            )
            _ = display.ax_.set_title(f"2-class Precision-Recall curve - {split_name}")
            os.makedirs(ARTIFACT_PATH + pr_path , exist_ok=True)
            plt.savefig(ARTIFACT_PATH + pr_path +f'pr-{split_name}.jpeg')
            mlflow.log_artifact(ARTIFACT_PATH + pr_path +f'pr-{split_name}.jpeg', artifact_path=pr_path[:-1])

            plot_density(
                predproba,
                y,
                ARTIFACT_PATH + dens_path,
                f'density-{split_name}.jpeg',
                threshold=0.75,
            )
            mlflow.log_artifact(ARTIFACT_PATH + dens_path +f'density-{split_name}.jpeg', artifact_path=dens_path[:-1])

            mlflow.log_metric(f"Brier-{split_name}", brier_score_loss(y,predproba))

     
        mlflow.sklearn.log_model(model, 'model')
        
        # mlflow.log_param(
        #     "OOT_date", min(pd.to_datetime(dataset.X_oot["Datum"], dayfirst=True))
        # )
    
        print(type(model))
        pickle.dump(model, open("model.pkl", 'wb'))
        mlflow.log_artifact('model.pkl')
        mlflow.log_artifact("conf\config.yaml")
        # mlflow.log_params(cfg.model.model_params)
        # mlflow.log_param("feature_depth", cfg.model.feature_depth)


if __name__ == "__main__":
    main()
