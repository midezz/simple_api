import inspect
import os
from random import choices

import pytest
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy_utils import create_database, drop_database

from simplerestapi.endpoint import ConfigEndpoint, Endpoint
from tests import models

from .models import Base

ERROR_TEMPLATE = 'Model \'{0}\' has incorrect ConfigEndpoint parameter \'{1}\': {2}'


class TestExampleConfigEndpoint:
    def __init__(self):
        self.denied_methods = ['get', 'delete']
        self.pagination = 20
        self.path = '/test_path'
        self.exclude_fields = ['id']
        self.join_related = True


class ModelTest(models.Base, Endpoint):
    id = Column(Integer, primary_key=True)

    class ConfigEndpoint:
        denied_methods = ['get', 'delete']
        pagination = 20
        path = '/test_path'
        exclude_fields = ['id']
        join_related = True


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
def db_url_test(db_url):
    return db_url + '_' + ''.join(choices('0123456789', k=20))


@pytest.fixture(scope='session')
def db_url():
    return os.environ.get('DB_URL')


@pytest.fixture(scope='session')
def engine(db_url_test):
    return create_engine(db_url_test)


@pytest.fixture(scope='session')
def db_setup(db_url_test, engine):
    create_database(db_url_test)
    Base.metadata.create_all(engine)
    yield
    drop_database(db_url_test)


@pytest.fixture(autouse=True)
def reset_models_settings():
    yield
    for _, member in inspect.getmembers(models):
        if inspect.isclass(member) and Endpoint in member.__bases__:
            member._set_default_config()
    setattr(
        ModelTest,
        'ConfigEndpoint',
        ConfigEndpoint(current_config=TestExampleConfigEndpoint()),
    )
