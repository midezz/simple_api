import pytest


@pytest.mark.parametrize(
    'configuration_endpoint, expected_errors',
    (
        ({}, []),
        (
            {'pagination': 'test', 'path': []},
            [
                'Model \'ModelTest\' has incorrect ConfigEndpoint parameter \'pagination\': value is not a valid integer',
                'Model \'ModelTest\' has incorrect ConfigEndpoint parameter \'path\': str type expected',
            ],
        ),
        (
            {'denied_methods': 10},
            [
                'Model \'ModelTest\' has incorrect ConfigEndpoint parameter \'denied_methods\': value is not a valid list',
            ],
        ),
        (
            {'exclude_fields': 'test'},
            [
                'Model \'ModelTest\' has incorrect ConfigEndpoint parameter \'exclude_fields\': value is not a valid list',
            ],
        ),
        (
            {'denied_methods': ['not_exists_method']},
            [
                'Model \'ModelTest\' has incorrect ConfigEndpoint parameter \'denied_methods\': methods must be from list (\'get\', \'post\', \'delete\', \'put\', \'patch\')',
            ],
        ),
    ),
)
def test_validate_config_endpoint(
    configuration_endpoint, expected_errors, configured_model
):
    for key, val in configuration_endpoint.items():
        setattr(configured_model.ConfigEndpoint, key, val)
    errors = configured_model.validate_model()
    assert errors == expected_errors
