# -*- coding: utf-8 -*-
import sys
from typing import List, Optional
import click
import logging
from pathlib import Path
import json
import pickle

import pandas as pd

try:
    from ml_project.entities import read_training_pipeline_params
except ModuleNotFoundError:
    project_dir = Path(__file__).resolve().parents[3]
    sys.path.append(str(project_dir))
    from ml_project.entities import read_training_pipeline_params


def predict(
        model,
        dataset: pd.DataFrame,
):
    result = model.predict_proba(dataset)
    return result[:, 1]


@click.command()
@click.argument('config_filepath', type=click.Path(exists=True))
@click.argument('dataset_filepath', type=click.Path(exists=True))
@click.argument('predict_dataset_filepath')
def main(config_filepath, dataset_filepath, predict_dataset_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    params = read_training_pipeline_params(config_filepath)

    logger = logging.getLogger(__name__)
    logger.info(
        f'predict with model {params.output_model_path} on dataset {dataset_filepath}'
    )

    with open(params.output_model_path, 'wb') as f_in:
        model = pickle.load(f_in)

    with open(params.report_path, 'r') as f_in:
        report = json.load(f_in)

    df = pd.read_csv(dataset_filepath)
    logger.debug(f'dataset downloaded with shape {df.shape}')

    df['predict'] = predict(model, df[report['features']])

    logger.info('prediction completed')
    df.to_csv(predict_dataset_filepath, index=False)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    main()
