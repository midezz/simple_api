import pytest

from simple_api.url_params import UrlParams
from tests.models import CustomUser


@pytest.mark.parametrize(
    'filters, errors',
    (
        ({'name': 'test'}, []),
        ({'name__gte': 'test'}, []),
        ({'name__lte': 'test'}, []),
        ({'name__gt': 'test'}, []),
        ({'name__lt': 'test'}, []),
        ({'bla': 'test'}, ['Filter \'bla\' is not valid']),
        ({'name__bla': 'test'}, ['Filter \'name__bla\' is not valid']),
        (
            {'name__bla': 'test', 'bla': 'test'},
            ['Filter \'name__bla\' is not valid', 'Filter \'name__bla\' is not valid'],
        ),
    ),
)
def test_validate_filters(filters, errors):
    params = UrlParams(CustomUser, filters)
    params.valid_filters()
    assert len(errors) == len(params.errors)
    for error in errors:
        assert error in params.errors


@pytest.mark.parametrize(
    'order, errors',
    (
        ({'order': 'id'}, []),
        ({'order': '-id'}, []),
        ({'order': 'test'}, ['Order by \'test\' is not valid']),
        ({'order': '-test'}, ['Order by \'-test\' is not valid']),
    ),
)
def test_valid_order(order, errors):
    params = UrlParams(CustomUser, order)
    params.valid_order()
    assert params.errors == errors


@pytest.mark.parametrize(
    'limit, errors',
    (
        ({'limit': 10}, []),
        ({'limit': 'a'}, ['Limit parameter \'a\' is not correct']),
    ),
)
def test_valid_number_parameter(limit, errors):
    params = UrlParams(CustomUser, limit)
    params.valid_number_parameter(params.limit_param, 'Limit')
    assert params.errors == errors


@pytest.mark.parametrize(
    'params, expected, errors',
    (
        ({'name': 'test'}, True, []),
        ({'name__gte': 'test'}, True, []),
        ({'order': 'name'}, True, []),
        ({'limit': 10}, True, []),
        ({'limit': 'a'}, False, ['Limit parameter \'a\' is not correct']),
        ({'order': 'test'}, False, ['Order by \'test\' is not valid']),
        ({'bla': 'test'}, False, ['Filter \'bla\' is not valid']),
        (
            {'name__bla': 'test', 'order': 'test', 'limit': 'a'},
            False,
            [
                'Filter \'name__bla\' is not valid',
                'Order by \'test\' is not valid',
                'Limit parameter \'a\' is not correct',
            ],
        ),
    ),
)
def test_is_valid(params, expected, errors):
    params = UrlParams(CustomUser, params)
    assert params.is_valid() == expected
    assert len(params.errors) == len(errors)
    for error in errors:
        error in params.errors


@pytest.mark.parametrize(
    'order, expected',
    (
        ({'order': 'age'}, CustomUser.age),
        ({}, None),
    ),
)
def test_order(order, expected):
    params = UrlParams(CustomUser, order)
    assert params.order_by is expected


def test_columns():
    params = UrlParams(CustomUser, {})
    assert params.columns == ['id', 'name', 'surname', 'age']
