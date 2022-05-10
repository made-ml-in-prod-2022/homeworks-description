# -*- coding: utf-8 -*-
import sys
from typing import List, Optional
import click
import logging
from pathlib import Path
import json

import pandas as pd

try:
    from ml_project.entities import read_training_pipeline_params
except ModuleNotFoundError:
    project_dir = Path(__file__).resolve().parents[3]
    sys.path.append(str(project_dir))
    from ml_project.entities import read_training_pipeline_params

# from dotenv import find_dotenv, load_dotenv

INTERIM_DATA_FILEPATH = './data/interim'
PROCESSED_DATA_FILEPATH = './data/processed'


class CatFeatureTargetEncoder:
    def __init__(
            self,
            cat_feature_list: List[str],
            target_name: str,
            logger: logging.Logger,
            min_count: Optional[int] = None,
            inplace: bool = False
    ):
        self.cat_feature_list = cat_feature_list
        self.target_name = target_name
        self.inplace = inplace
        self.logger = logger
        self.encoded_dicts = dict()
        self.min_count = min_count

    def fit(self, dataset):
        for feature_name in self.cat_feature_list:
            encoded_dict = self._build_encoded_dict(dataset, feature_name)
            self.encoded_dicts.update(encoded_dict)

        self.logger.info(f'{id(self)} fitted')

        return self

    def transform(self, dataset):
        dataset_ = dataset.copy()
        if self.inplace:
            for feature_name in self.cat_feature_list:
                dataset_[feature_name] = dataset_[feature_name]\
                    .map(self.encoded_dicts[feature_name])
            self.logger.info('cat feature transformed inplace')
        else:
            for feature_name in self.cat_feature_list:
                dataset_[f'{feature_name}_mt'] = dataset_[feature_name] \
                    .map(self.encoded_dicts[feature_name])
            self.logger.info('transformed cat feature store in columns with suffix "_mt"')

        return dataset_

    def _build_encoded_dict(
            self,
            dataset: pd.DataFrame,
            feature_name: str
    ):
        min_count = self.min_count or dataset.shape[0] * .05
        vc_series = dataset[feature_name].value_counts() >= min_count
        vc_df = vc_series.reset_index().rename(
            columns={feature_name: 'vc', 'index': feature_name}
        )
        mean_target_df = dataset[[feature_name, self.target_name]]\
            .groupby(feature_name)\
            .mean()\
            .reset_index()

        df = mean_target_df.merge(vc_df, on=feature_name)
        df_ = df[df['vc']].drop(columns=['vc'])

        if df_[self.target_name].max() == 1:
            self.logger.warning('there is a cat value with only first class presented')
        elif df_[self.target_name].min() == 0:
            self.logger.warning('there is a cat value with only zero class presented')

        df_final = df_.rename(
            columns={feature_name: 'index', self.target_name: feature_name}
        ).set_index('index')
        result_dict = df_final.to_dict()

        return result_dict


@click.command()
@click.argument('config_filepath', type=click.Path(exists=True))
def main(config_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('build new features with CatFeatureTargetEncoder')
    logger.info(f'read params from {config_filepath}')

    params = read_training_pipeline_params(config_filepath)

    dataset_name = Path(params.input_data_path).stem
    interim_data_path = f'{INTERIM_DATA_FILEPATH}/{dataset_name}_split.csv'

    logger.info(f'read interim data from {interim_data_path}')

    df = pd.read_csv(interim_data_path)

    logger.debug(
        f'split raw data into train-valid-test datasets with params: {params.splitting_params}'
    )

    cft_encoder = CatFeatureTargetEncoder(
        cat_feature_list=params.feature_params.categorical_features,
        target_name=params.feature_params.target_name,
        logger=logger,
        inplace=params.feature_params.build_features_inplace
    )

    train_mask = ~df['test_flag'] & ~df['val_flag']
    val_mask = df['val_flag']
    test_mask = df['test_flag']

    cft_encoder = cft_encoder.fit(df[train_mask])

    train = cft_encoder.transform(df[train_mask])
    val = cft_encoder.transform(df[val_mask])
    test = cft_encoder.transform(df[test_mask])

    df_encoded = pd.concat([train, val, test])
    encoded_dataset_filepath = \
        f'{PROCESSED_DATA_FILEPATH}/{dataset_name}_prepared.csv'

    features = list(
        set(df_encoded.columns) - {params.feature_params.target_name}
    )
    categorical_features = list(
        set(df_encoded.columns) & set(params.feature_params.categorical_features)
    )

    logger.info(f'final dataset features: {features}')
    logger.info(f'final dataset cat features: {categorical_features}')

    report = {}
    report.update(
        {
            'features': features,
            'categorical_features': categorical_features,
            'target': params.feature_params.target_name
         }
    )

    with open(params.report_path, 'w') as f_out:
        json.dump(report, f_out, indent=4)

    df_encoded.to_csv(encoded_dataset_filepath, index=False)
    logger.info(f'processed dataset saved in {encoded_dataset_filepath}')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    main()
