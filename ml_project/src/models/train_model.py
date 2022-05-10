# -*- coding: utf-8 -*-
import sys
from typing import List, Optional
import click
import logging
from pathlib import Path
import json
import pickle

import pandas as pd
from lightgbm import LGBMClassifier, early_stopping
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score

try:
    from ml_project.src.models.predict_model import predict
    from ml_project.entities import read_training_pipeline_params, TrainingPipelineParams
except ModuleNotFoundError:
    project_dir = Path(__file__).resolve().parents[3]
    sys.path.append(str(project_dir))
    from ml_project.src.models.predict_model import predict
    from ml_project.entities import read_training_pipeline_params, TrainingPipelineParams

PROCESSED_DATA_FILEPATH = './data/processed'


def train(
        train_dataset: pd.DataFrame,
        val_dataset: pd.DataFrame,
        params: TrainingPipelineParams,
        features: List,
        categorical_features: List,
        target: str,
):

    if params.train_params.model == 'lightgbm':
        model = LGBMClassifier(
            random_state=params.train_params.random_state,
            **params.train_params.param_dict
        )
        model.fit(
            X=train_dataset[features],
            y=train_dataset[target],
            feature_name=features,
            categorical_feature=categorical_features,
            eval_set=[(val_dataset[features], val_dataset[target])],
            eval_metric='roc_auc',
            callbacks=[early_stopping(5)]
        )

    elif params.train_params.model == 'catboost':
        model = CatBoostClassifier(
            random_state=params.train_params.random_state,
            eval_metric='AUC',
            **params.train_params.param_dict
        )
        model.fit(
            X=train_dataset[features],
            y=train_dataset[target],
            cat_features=categorical_features,
            eval_set=[(val_dataset[features], val_dataset[target])],
            early_stopping_rounds=5
        )
    else:
        raise NotImplementedError

    return model


@click.command()
@click.argument('config_filepath', type=click.Path(exists=True))
def main(config_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('train model')
    logger.info(f'read params from {config_filepath}')

    params = read_training_pipeline_params(config_filepath)

    dataset_name = Path(params.input_data_path).stem
    processed_data_path = f'{PROCESSED_DATA_FILEPATH}/{dataset_name}_prepared.csv'

    logger.info(f'read prepared data from {processed_data_path}')

    df = pd.read_csv(processed_data_path)

    train_mask = ~df['test_flag'] & ~df['val_flag']
    val_mask = df['val_flag']
    test_mask = df['test_flag']

    with open(params.report_path, 'r') as f_in:
        report = json.load(f_in)

    features = report['features']
    categorical_features = report['categorical_features']
    target = report['target']

    model = train(
        train_dataset=df[train_mask],
        val_dataset=df[val_mask],
        params=params,
        features=features,
        categorical_features=categorical_features,
        target=target,
    )

    train_score = roc_auc_score(
        df[train_mask][target],
        predict(model, df[train_mask][features])
    )
    val_score = roc_auc_score(
        df[val_mask][target],
        predict(model, df[val_mask][features])
    )
    test_score = roc_auc_score(
        df[test_mask][target],
        predict(model, df[test_mask][features])
    )

    metrics = {
        'train_roc_auc_score': train_score,
        'val_roc_auc_score': val_score,
        'test_roc_auc_score': test_score,
    }
    with open(params.report_path, 'r') as f_in:
        report = json.load(f_in)

    report.update(metrics)
    report.update({'config_filepath': config_filepath})
    report.update({'model_params': model.get_params()})

    with open(params.report_path, 'w') as f_out:
        json.dump(report, f_out, indent=4)

    logger.info(f'metrics {metrics} saved in {params.report_path}')
    logger.info(f'train {params.train_params.model} model finished')

    with open(params.output_model_path, 'wb') as f_out:
        pickle.dump(model, f_out)

    logger.info(
        f'result {params.train_params.model} model saved in {params.output_model_path}'
    )


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    main()
