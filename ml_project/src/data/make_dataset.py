# -*- coding: utf-8 -*-
import sys
from typing import Tuple
import click
import logging
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

try:
    from ml_project.entities import read_training_pipeline_params
except ModuleNotFoundError:
    project_dir = Path(__file__).resolve().parents[3]
    sys.path.append(str(project_dir))
    from ml_project.entities import read_training_pipeline_params

# from dotenv import find_dotenv, load_dotenv

INTERIM_DATA_FILEPATH = './data/interim'


def make_train_valid_test(
        df: pd.DataFrame,
        test_size: float,
        val_size: float,
        target_name: str,
        random_state: int
) -> Tuple[pd.DataFrame, ...]:
    data, test = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df[target_name]
    )
    train, valid = train_test_split(
        data,
        test_size=val_size,
        random_state=random_state,
        stratify=data[target_name]
    )

    return train, valid, test


@click.command()
@click.argument('config_filepath', type=click.Path(exists=True))
def main(config_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    logger.info(f'read params from {config_filepath}')
    params = read_training_pipeline_params(config_filepath)

    logger.info(f'read raw data from {params.input_data_path}')
    df = pd.read_csv(params.input_data_path)

    logger.debug(
        f'split raw data into train-valid-test datasets with params: {params.splitting_params}'
    )
    train, valid, test = make_train_valid_test(
        df,
        test_size=params.splitting_params.test_size,
        val_size=params.splitting_params.val_size,
        target_name=params.feature_params.target_name,
        random_state=params.splitting_params.random_state
    )

    train['test_flag'] = False
    train['val_flag'] = False

    valid['test_flag'] = False
    valid['val_flag'] = True

    test['test_flag'] = True
    test['val_flag'] = False

    logger.debug(f'train size: {train.size}, '
                 f'mean target: {train[params.feature_params.target_name].mean()}')
    logger.debug(f'valid size: {valid.size},'
                 f' mean target {valid[params.feature_params.target_name].mean()}')
    logger.debug(f'test size: {test.size},'
                 f' mean target {test[params.feature_params.target_name].mean()}')

    df_ = pd.concat([train, valid, test])

    dataset_name = Path(params.input_data_path).stem
    split_dataset_filepath = f'{INTERIM_DATA_FILEPATH}/{dataset_name}_split.csv'

    df_.to_csv(split_dataset_filepath, index=False)

    logger.info(f'split data saved in {split_dataset_filepath}')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    main()
