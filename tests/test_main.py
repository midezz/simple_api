import pytest

from simplerestapi.api import GetUpdateDeleteAPI, ListCreateAPI
from simplerestapi.exception import ConfigEndpointError
from simplerestapi.main import SimpleApi
from tests import models

from .conftest import ERROR_TEMPLATE


class TestMain:
    @pytest.fixture(autouse=True)
    def setup(self, db_url_test):
        self.simple_api = SimpleApi(models, db_url_test)

    def test_get_models(self):
        assert len(self.simple_api.models) == 2
        assert models.Car in self.simple_api.models
        assert models.CustomUser in self.simple_api.models

    def test_construct_routes(self):
        expect_routes = [
            {'path': '/car', 'endpoint': ListCreateAPI, 'model': models.Car},
            {'path': '/car/{id}', 'endpoint': GetUpdateDeleteAPI, 'model': models.Car},
            {
                'path': '/customuser',
                'endpoint': ListCreateAPI,
                'model': models.CustomUser,
            },
            {
                'path': '/customuser/{id}',
                'endpoint': GetUpdateDeleteAPI,
                'model': models.CustomUser,
            },
        ]
        assert len(self.simple_api.routes) == 4
        result = [{'path': r.path, 'endpoint': r.endpoint, 'model': r.model} for r in self.simple_api.routes]
        for expect in expect_routes:
            assert expect in result


def test_raise_exceptions_by_errors(db_url_test):
    models.Car.ConfigEndpoint.pagination = 'not int'
    models.CustomUser.ConfigEndpoint.denied_methods = ['not_exist_method']
    with pytest.raises(ConfigEndpointError) as exc:
        SimpleApi(models, db_url_test)
    expected_errors = [
        ERROR_TEMPLATE.format('Car', 'pagination', 'value is not a valid integer'),
        ERROR_TEMPLATE.format(
            'CustomUser',
            'denied_methods',
            'methods must be from list (\'get\', \'post\', \'delete\', \'put\', \'patch\')',
        ),
    ]
    assert exc.value.args[0] == 'Your models have errors:\n' + '\n'.join(expected_errors)
    assert exc.value.errors == expected_errors
