from random import choices
import inspect

import pytest
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy_utils import create_database, drop_database

from simple_api.endpoint import Endpoint
from simple_api.main import SimpleApi
from tests import models
from simple_api.endpoint import ConfigEndpoint


from .models import Base


class ModelTest(models.Base, Endpoint):
    id = Column(Integer, primary_key=True)

    class ConfigEndpoint:
        denied_methods = ['get', 'delete']
        pagination = 20
        path = '/test_path'
        exclude_fields = ['id']


@pytest.fixture
def not_config_model():
    return models.CustomUser


@pytest.fixture
def module_models():
    return models


@pytest.fixture
def configured_model():
    return ModelTest


@pytest.fixture(scope='session')
def db_url():
    db = 'postgresql://pydantic_orm:123456@127.0.0.1'
    db_name = 'test_' + ''.join(choices('0123456789', k=20))
    url = f'{db}/{db_name}'
    return url


@pytest.fixture(scope='session')
def engine(db_url):
    return create_engine(db_url)


@pytest.fixture(scope='session')
def db_setup(db_url, engine):
    create_database(db_url)
    Base.metadata.create_all(engine)
    yield
    drop_database(db_url)


@pytest.fixture(scope='module')
def simple_api():
    return SimpleApi(
            models, 'postgresql://pydantic_orm:123456@127.0.0.1/pydantic_test'
        )


@pytest.fixture(autouse=True)
def reset_models_settings():
    yield
    for _, member in inspect.getmembers(models):
        if inspect.isclass(member) and Endpoint in member.__bases__:
            setattr(member, 'ConfigEndpoint', ConfigEndpoint())
