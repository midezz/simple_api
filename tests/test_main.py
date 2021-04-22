import pytest

from src.simplerestapi.api import GetUpdateDeleteAPI, ListCreateAPI
from src.simplerestapi.main import SimpleApi
from tests import models


class TestMain:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.simple_api = SimpleApi(
            models, 'postgresql://pydantic_orm:123456@127.0.0.1/pydantic_test'
        )

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
        result = [
            {'path': r.path, 'endpoint': r.endpoint, 'model': r.model}
            for r in self.simple_api.routes
        ]
        for expect in expect_routes:
            assert expect in result
