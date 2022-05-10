import pytest

from ..src.data.make_dataset import make_train_valid_test


def test_make_train_valid_test(dataset):
    train, valid, test = make_train_valid_test(
        dataset,
        test_size=0.1,
        val_size=0.1,
        random_state=0,
        target_name='target'
    )
    train_valid_intersection_count = train.merge(valid, on='id').shape[0]
    train_test_intersection_count = train.merge(test, on='id').shape[0]
    test_valid_intersection_count = test.merge(valid, on='id').shape[0]

    assert not train_valid_intersection_count, \
        f'intersection train and valid should equal 0,' \
        f' but equal {train_valid_intersection_count}'
    assert not train_test_intersection_count, \
        f'intersection train and test should equal 0, ' \
        f'but equal {train_test_intersection_count}'
    assert not test_valid_intersection_count, \
        f'intersection valid and test should equal 0, ' \
        f'but equal {test_valid_intersection_count}'

    assert pytest.approx(round(train['target'].mean(), 3), ) ==\
           round(valid['target'].mean(), 3), 'data split should be stratified by target'
