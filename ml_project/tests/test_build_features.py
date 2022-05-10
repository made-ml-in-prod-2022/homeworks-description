import sys
import pytest
from pathlib import Path

try:
    from ml_project.src.features.build_features import CatFeatureTargetEncoder
except ModuleNotFoundError:
    project_dir = Path(__file__).resolve().parents[3]
    sys.path.append(str(project_dir))
    from ml_project.src.features.build_features import CatFeatureTargetEncoder


def test_cat_feature_target_encoder_class_default(dataset, logger, caplog):
    cft_encoder = CatFeatureTargetEncoder(
        cat_feature_list=['cat_feature'],
        target_name='det_target',
        logger=logger,
    )
    encoded_dict = cft_encoder._build_encoded_dict(dataset, 'cat_feature')

    assert isinstance(encoded_dict, dict), \
        f'encoded_dict should be dict type, but given {type(encoded_dict)} object'
    assert 'cat_feature' in encoded_dict.keys(), \
        """
        encoded_dict should be implemented as 
        {"feature_name": encoded_dict_cat_values}
        """
    assert isinstance(encoded_dict['cat_feature'], dict), \
        """
        encoded_dict should be implemented as 
        {"feature_name": encoded_dict_cat_values}
        """
    assert all(
        [k in encoded_dict['cat_feature'].keys() for k in [0, 1]]
    ), 'only cat_feature values with count eq. or more than min_count should be presented'

    assert .2 == encoded_dict['cat_feature'][0]
    assert 1 == encoded_dict['cat_feature'][1]

    assert 'WARNING' in caplog.text, \
        'logger should get WARNING when mean target ' \
        'equal 1 or 0 within some cat feature value'


@pytest.mark.parametrize(
    'inplace, encode_feature_name',
    [
        pytest.param(True, 'cat_feature', id='inplace'),
        pytest.param(False, 'cat_feature_mt', id='not inplace')
    ]
)
def test_cat_feature_target_encoder_class_fit_transform(
        inplace, encode_feature_name, dataset, logger, caplog
):
    cft_encoder = CatFeatureTargetEncoder(
        cat_feature_list=['cat_feature'],
        target_name='det_target',
        logger=logger,
        inplace=inplace
    )
    cft_encoder = cft_encoder.fit(dataset)

    assert cft_encoder.encoded_dicts is not None

    dataset_ = cft_encoder.transform(dataset)
    assert encode_feature_name in dataset_.columns
    assert .2 == dataset_[encode_feature_name][0]
