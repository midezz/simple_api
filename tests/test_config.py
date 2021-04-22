from src.simplerestapi.endpoint import ConfigEndpoint


def test_get_attrs():
    expect = {
        'denied_methods': [],
        'pagination': 100,
        'path': None,
        'exclude_fields': [],
    }
    assert ConfigEndpoint.get_attrs() == expect


def test_config_endpoint(configured_model):
    assert configured_model.ConfigEndpoint.denied_methods == ['get', 'delete']
    assert configured_model.ConfigEndpoint.pagination == 20
    assert configured_model.ConfigEndpoint.path == '/test_path'
    assert configured_model.ConfigEndpoint.exclude_fields == ['id']


def test_default_config_endpoint(not_config_model):
    for attr, val in ConfigEndpoint.get_attrs().items():
        getattr(not_config_model.ConfigEndpoint, attr) == val
