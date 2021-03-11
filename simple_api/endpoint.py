from sqlalchemy.ext.declarative import declared_attr

from .api import HANDLER_CLASS, HANDLER_CLASS_LISTCREATE, GetUpdateDeleteAPI
from .router import SimpleApiRouter


class Endpoint:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    class ConfigEndpoint:
        pegination = 100
        denied_methods = []

    @classmethod
    def get_listcreate_routes(cls, session):
        allowed_methods = []
        if 'post' not in cls.ConfigEndpoint.denied_methods:
            allowed_methods.append('post')
        if cls.ConfigEndpoint.pegination > 0:
            allowed_methods.append('list')
        if len(allowed_methods) == 0:
            return None
        path = '/' + cls.__tablename__
        allowed_methods.sort()
        handler_class = HANDLER_CLASS_LISTCREATE[tuple(allowed_methods)]
        return SimpleApiRouter(cls, session, path, handler_class)

    @classmethod
    def get_handler_class(cls):
        denied_methods = cls.ConfigEndpoint.denied_methods[:]
        if 'post' in denied_methods:
            denied_methods.remove('post')
        if len(denied_methods) == 3:
            return None
        denied_methods.sort()
        denied_methods = tuple(denied_methods)
        return HANDLER_CLASS.get(denied_methods, GetUpdateDeleteAPI)

    @classmethod
    def get_other_routes(cls, session):
        handler_class = cls.get_handler_class()
        if not handler_class:
            return None
        path = '/' + cls.__tablename__ + '/{id}'
        return SimpleApiRouter(cls, session, path, handler_class)

    @classmethod
    def get_columns_values(cls, model):
        columns = [c.name for c in cls.__table__.columns]
        return {column: getattr(model, column) for column in columns}
