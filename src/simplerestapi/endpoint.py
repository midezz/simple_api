from sqlalchemy.ext.declarative import DeclarativeMeta, declared_attr

from .api import HANDLER_CLASS_LISTCREATE, GetUpdateDeleteAPI
from .router import SimpleApiRouter


class Endpoint:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def get_path(cls):
        if cls.ConfigEndpoint.path:
            return cls.ConfigEndpoint.path
        return '/' + cls.__tablename__

    @classmethod
    def get_listcreate_routes(cls):
        allowed_methods = []
        if 'post' not in cls.ConfigEndpoint.denied_methods:
            allowed_methods.append('post')
        if cls.ConfigEndpoint.pagination > 0:
            allowed_methods.append('list')
        if len(allowed_methods) == 0:
            return None
        allowed_methods.sort()
        handler_class = HANDLER_CLASS_LISTCREATE[tuple(allowed_methods)]
        path = cls.get_path()
        return SimpleApiRouter(cls, path, handler_class)

    @classmethod
    def get_handler_class(cls):
        denied_methods = cls.ConfigEndpoint.denied_methods[:]
        if 'post' in denied_methods:
            denied_methods.remove('post')
        if len(denied_methods) == 4:
            return None
        return GetUpdateDeleteAPI

    @classmethod
    def get_other_routes(cls):
        handler_class = GetUpdateDeleteAPI
        path = cls.get_path() + '/{id}'
        return SimpleApiRouter(cls, path, handler_class)

    @classmethod
    def get_columns_values(cls, model):
        columns = [
            c.name
            for c in cls.__table__.columns
            if c.name not in cls.ConfigEndpoint.exclude_fields
        ]
        return {column: getattr(model, column) for column in columns}


class ConfigEndpoint:
    pagination = 100
    denied_methods = []
    path = None
    exclude_fields = []

    @classmethod
    def get_attrs(cls):
        return {
            attr: getattr(cls, attr)
            for attr in cls.__dict__
            if attr.find('__') == -1 and attr != 'get_attrs'
        }


class ConstructEndpoint(DeclarativeMeta):
    def __new__(mcl, name, base, namespace, **kwargs):
        if Endpoint in base:
            if not namespace.get('ConfigEndpoint'):
                namespace['ConfigEndpoint'] = ConfigEndpoint()
            else:
                for attr, val in ConfigEndpoint.get_attrs().items():
                    if not hasattr(namespace['ConfigEndpoint'], attr):
                        setattr(namespace['ConfigEndpoint'], attr, val)
        return super().__new__(mcl, name, base, namespace, **kwargs)
