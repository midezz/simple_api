import pytest

from .conftest import ERROR_TEMPLATE


@pytest.mark.parametrize(
    'configuration_endpoint, expected_errors',
    (
        ({}, []),
        (
            {'not_support_parameter': 10},
            [ERROR_TEMPLATE.format('ModelTest', 'not_support_parameter', 'not support parameters')],
        ),
        (
            {'pagination': 'test', 'path': []},
            [
                ERROR_TEMPLATE.format('ModelTest', 'pagination', 'value is not a valid integer'),
                ERROR_TEMPLATE.format('ModelTest', 'path', 'str type expected'),
            ],
        ),
        (
            {'denied_methods': 10},
            [ERROR_TEMPLATE.format('ModelTest', 'denied_methods', 'value is not a valid list')],
        ),
        (
            {'exclude_fields': 'test'},
            [ERROR_TEMPLATE.format('ModelTest', 'exclude_fields', 'value is not a valid list')],
        ),
        (
            {'denied_methods': ['not_exists_method']},
            [
                ERROR_TEMPLATE.format(
                    'ModelTest',
                    'denied_methods',
                    'methods must be from list (\'get\', \'post\', \'delete\', \'put\', \'patch\')',
                )
            ],
        ),
        (
            {'pagination': -2},
            [ERROR_TEMPLATE.format('ModelTest', 'pagination', 'value must be above or equal 0')],
        ),
    ),
)
def test_validate_config_endpoint(configuration_endpoint, expected_errors, configured_model):
    for key, val in configuration_endpoint.items():
        setattr(configured_model.ConfigEndpoint, key, val)
    errors = configured_model.validate_model()
    assert errors == expected_errors
