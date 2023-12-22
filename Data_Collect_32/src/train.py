
import mlflow

from hydra import compose, initialize
from hydra.utils import instantiate
import pandas as pd
import pickle
from Data_Collect_32.process_data.dataset import Dataset
from Data_Collect_32.process_data.data_splitter import data_splitter
from Data_Collect_32.Evaluate.pips import get_pips_margin
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.calibration import calibration_curve


PATH = './data/Data_collect_32.csv'


def main():

    initialize(config_path="../conf/")
    cfg = compose(config_name='config.yaml')
    with mlflow.start_run(experiment_id="243908727313542997", run_name='test') as run:

        # Define pipeline
        pipeline = instantiate(cfg.data_pipeline)
        df = pd.read_csv(PATH)
        df = pipeline.apply(df.copy())
        model_features = create_window_list(cfg.model.feature_depth)
        dataset = Dataset(data = df, data_splitter = data_splitter)
        clf = HistGradientBoostingClassifier( **cfg.model.model_params)
        model = clf.fit(dataset.X_train[model_features], 
                        dataset.y_train, 
                        sample_weight = dataset.X_train['sample_weight'])
        pred_oot = model.predict(dataset.X_oot[model_features])
        mlflow.log_metric('Pips',get_pips_margin(pred_oot,
                                                    dataset.X_oot['next_close_price'],
                                                     dataset.X_oot['close_price'] ) )
        
        calibrated_clf = CalibratedClassifierCV(clf, cv='prefit')
        calibrated_clf.fit(dataset.X_train[model_features], dataset.y_train)
        pred_calibrated = calibrated_clf.predict_proba(dataset.X_oot[model_features]).T[1]
        threshold = max(calibration_curve(dataset.y_test, calibrated_clf.predict_proba(dataset.X_test[model_features]).T[1])[1])
        mlflow.log_metric('Pips calibrated',get_pips_margin(pred_calibrated,
                                                    dataset.X_oot['next_close_price'],
                                                     dataset.X_oot['close_price'] ,
                                                    threshold = threshold ))


        mlflow.log_artifact("conf\config.yaml")
        mlflow.log_params(cfg.model.model_params)
        mlflow.log_param('feature_depth', cfg.model.feature_depth)
        


def create_window_list(window: int )-> list:
    model_features = [ 'rsi', 'mfi', 'regrs', 'cci', 'is_in_time']
    model_features += ['rsi_norm_' + str(i) for i in range(0,window)]
    model_features += ['mfi_norm_' + str(i) for i in range(0,window)]
    model_features += ['williams_' + str(i) for i in range(0,window)]
    # model_features += ['tv_norm_' + str(i) for i in range(0,window)]
    model_features += ['regrs_norm_' + str(i) for i in range(0,window)]
    model_features += ['sma_norm_' + str(i) for i in range(0,window)]
    model_features += ['cci_norm_' + str(i) for i in range(0,window)]
    return model_features

if __name__ == "__main__":
    main()