import sys
import pytest
from pathlib import Path

from sklearn.model_selection import train_test_split

project_dir = Path(__file__).resolve().parents[3]
sys.path.append(str(project_dir))

try:
    from ml_project.src.models.train_model import train
    from ml_project.src.models.predict_model import predict
    from ml_project.entities import read_training_pipeline_params
except ModuleNotFoundError:
    project_dir = Path(__file__).resolve().parents[3]
    sys.path.append(str(project_dir))
    from ml_project.src.models.train_model import train
    from ml_project.src.models.predict_model import predict
    from ml_project.entities import read_training_pipeline_params


COMPLETE_CONFIG_PATH = './tests/test_configs/complete_config.yaml'


@pytest.mark.parametrize(
    'model_type',
    [
        pytest.param('lightgbm', id='lightgbm'),
        pytest.param('catboost', id='catboost')
    ]
)
def test_train_predict(model_type, dataset):
    params = read_training_pipeline_params(COMPLETE_CONFIG_PATH)
    params.train_params.model = model_type
    train_dataset, val_dataset = train_test_split(dataset, test_size=0.2)
    model = train(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        params=params,
        features=['id', 'target', 'cat_feature'],
        categorical_features=['cat_feature'],
        target='det_target',
    )

    if model_type == 'lightgbm':
        assert model.fitted_
    else:
        assert model.is_fitted()

    val_dataset['predict'] = predict(
        model, val_dataset[['id', 'target', 'cat_feature']]
    )
    assert 'predict' in val_dataset.columns
    assert val_dataset['predict'].isna().sum() == 0
