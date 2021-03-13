import pytest
from sqlalchemy import Column, Integer

from simple_api import Endpoint
from tests import models


class ModelTest(models.Base, Endpoint):
    id = Column(Integer, primary_key=True)

    class ConfigEndpoint:
        denied_methods = ['get', 'delete']


@pytest.fixture
def single_model():
    return models.CustomUser


@pytest.fixture
def module_models():
    return models


@pytest.fixture
def class_modeltest():
    return ModelTest
