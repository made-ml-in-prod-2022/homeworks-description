import pytest
from marshmallow.exceptions import ValidationError

from ..entities import read_training_pipeline_params


INCOMPLETE_CONFIG_PATH = './tests/test_configs/incomplete_config.yaml'
COMPLETE_CONFIG_PATH = './tests/test_configs/complete_config.yaml'
WRONG_MODEL_CONFIG_PATH = './tests/test_configs/wrong_model_config.yaml'


def test_read_training_pipeline_params():
    read_training_pipeline_params(COMPLETE_CONFIG_PATH)


def test_read_training_pipeline_params_raise_error_when_required_params_missed():
    with pytest.raises(ValidationError):
        read_training_pipeline_params(INCOMPLETE_CONFIG_PATH)


def test_read_training_pipeline_params_raise_error_when_unsupported_model_given():
    with pytest.raises(ValidationError):
        read_training_pipeline_params(WRONG_MODEL_CONFIG_PATH)
