from simple_api.config import ConfigEndpoint


def test_get_attrs():
    expect = {'denied_methods': [], 'pagination': 100}
    assert ConfigEndpoint.get_attrs() == expect


def test_config_endpoint(class_modeltest):
    assert class_modeltest.ConfigEndpoint.denied_methods == ['get', 'delete']
    assert class_modeltest.ConfigEndpoint.pagination == 100


def test_default_config_endpoint(single_model):
    for attr, val in ConfigEndpoint.get_attrs().items():
        getattr(single_model.ConfigEndpoint, attr) == val
