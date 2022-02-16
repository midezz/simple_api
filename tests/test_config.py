import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from simplerestapi.endpoint import ConfigEndpoint, Endpoint

from .models import Base


def test_get_attrs():
    expect = {
        'denied_methods': [],
        'pagination': 100,
        'path': None,
        'exclude_fields': [],
        'join_related': [],
    }
    assert ConfigEndpoint().get_attrs() == expect


def test_config_endpoint(configured_model):
    assert configured_model.ConfigEndpoint.denied_methods == ['get', 'delete']
    assert configured_model.ConfigEndpoint.pagination == 20
    assert configured_model.ConfigEndpoint.path == '/test_path'
    assert configured_model.ConfigEndpoint.exclude_fields == ['id']
    assert configured_model.ConfigEndpoint.join_related == []


@pytest.mark.parametrize('join_related_parameter', (True, ['related_field']))
def test_join_related(join_related_parameter):
    class Test(Base, Endpoint):
        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True)

    class ModelTestJoinRelated(Base, Endpoint):
        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True)
        related_field = relationship('Test')

        class ConfigEndpoint:
            join_related = join_related_parameter

    assert ModelTestJoinRelated.ConfigEndpoint.join_related == ['related_field']


def test_default_config_endpoint(not_config_model):
    for attr, val in ConfigEndpoint().get_attrs().items():
        getattr(not_config_model.ConfigEndpoint, attr) == val
