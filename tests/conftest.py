import pytest
from tests import models


@pytest.fixture
def single_model():
    return models.CustomUser


@pytest.fixture
def module_models():
    return models
