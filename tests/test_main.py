import pytest

from simple_api.main import SimpleApi
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
