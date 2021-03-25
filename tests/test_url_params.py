import pytest

from simple_api.url_params import UrlParams
from tests.models import CustomUser


@pytest.mark.parametrize(
    'filters, expected, error',
    (
        ({'name': 'test'}, True, None),
        ({'name__gte': 'test'}, True, None),
        ({'name__lte': 'test'}, True, None),
        ({'name__gt': 'test'}, True, None),
        ({'name__lt': 'test'}, True, None),
        ({'bla': 'test'}, False, 'Filter \'bla\' is not valid'),
        ({'name__bla': 'test'}, False, 'Filter \'name__bla\' is not valid'),
    ),
)
def test_validate_filters(filters, expected, error):
    params = UrlParams(CustomUser, filters)
    assert params.valid_filters() == expected
    assert params.error == error


@pytest.mark.parametrize(
    'params, expected, error',
    (
        ({'name': 'test'}, True, None),
        ({'name__gte': 'test'}, True, None),
        ({'name__lte': 'test'}, True, None),
        ({'name__gt': 'test'}, True, None),
        ({'name__lt': 'test'}, True, None),
        ({'bla': 'test'}, False, 'Filter \'bla\' is not valid'),
        ({'name__bla': 'test'}, False, 'Filter \'name__bla\' is not valid'),
    ),
)
def test_is_valid(params, expected, error):
    params = UrlParams(CustomUser, params)
    assert params.is_valid() == expected
    assert params.error == error
