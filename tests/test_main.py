import pytest
from tests import models
from simple_api import SimpleApi
from simple_api import api


class TestMain:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.simple_api = SimpleApi(models)

    def test_get_models(self):
        assert len(self.simple_api.models) == 2
        assert models.Car in self.simple_api.models
        assert models.CustomUser in self.simple_api.models

    @pytest.mark.parametrize(
        'denied_methods, expected',
        (
            (['get', 'post'], 'UpdateDeleteAPI'),
            (['put', 'delete'], 'GetAPI'),
            (['get', 'post', 'delete'], 'UpdateAPI'),
            ([], 'GetUpdateDeleteAPI'),
            (['post', 'delete'], 'GetUpdateAPI'),
            (['put'], 'GetDeleteAPI'),
            (['put', 'get'], 'DeleteAPI'),
        )
    )
    def test_get_handler_class(self, denied_methods, expected):
        model = models.CustomUser
        model.ConfigEndpoint.denied_methods = denied_methods
        assert self.simple_api.get_handler_class(model).__name__ == expected
