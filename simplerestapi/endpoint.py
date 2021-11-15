from sqlalchemy.ext.declarative import DeclarativeMeta, declared_attr
from sqlalchemy.orm.relationships import RelationshipProperty

from .api import HANDLER_CLASS_LISTCREATE, GetUpdateDeleteAPI
from .model_validator import ModelValidator
from .router import SimpleApiRouter
from .utils import cached_property


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

    def get_columns_values(self, next_relative_level=True):
        columns = [c.name for c in self.__table__.columns if c.name not in self.ConfigEndpoint.exclude_fields]
        result = {column: getattr(self, column) for column in columns}
        if next_relative_level:
            result.update(self.retreive_related())
        return result

    def retreive_related(self):
        related = {}
        for field in self.ConfigEndpoint.join_related:
            model = getattr(self, field)
            if model is None:
                return {field: None}
            elif isinstance(model, list):
                related_values = [item.get_columns_values(next_relative_level=False) for item in model]
            else:
                related_values = model.get_columns_values(next_relative_level=False)
            related[field] = related_values
        return related

    @classmethod
    def get_joins(cls):
        return [getattr(cls, column) for column in cls.ConfigEndpoint.join_related]

    @classmethod
    def validate_model(cls):
        return ModelValidator(cls).errors

    @classmethod
    def _set_default_config(cls):
        setattr(cls, 'ConfigEndpoint', ConfigEndpoint())

    @classmethod
    def _config_endpoint(cls, **kwargs):
        for key, val in kwargs.items():
            setattr(cls.ConfigEndpoint, key, val)


class ConfigEndpoint:
    def __init__(self, current_config=None, namespace={}):
        self.pagination = 100
        self.denied_methods = []
        self.path = None
        self.exclude_fields = []
        self.namespace = namespace
        self.current_config = current_config
        if current_config:
            self.apply_config()

    def get_attrs(self):
        return {
            attr: getattr(self, attr)
            for attr in {'pagination', 'denied_methods', 'path', 'exclude_fields', 'join_related'}
            | self.current_config_attrs
        }

    @cached_property
    def current_config_attrs(self):
        if self.current_config is None:
            return set()
        return {
            attr for attr in self.current_config.__dict__ if attr.find('__') == -1 and attr not in ('join_related',)
        }

    def apply_config(self):
        for attr in self.current_config_attrs:
            parameter = getattr(self.current_config, attr, None)
            setattr(self, attr, parameter)

    @cached_property
    def join_related(self):
        if self.current_config is None:
            return []
        join_related = getattr(self.current_config, 'join_related', [])
        if join_related is True:
            return [field for field, val in self.namespace.items() if isinstance(val, RelationshipProperty)]
        return join_related


class ConstructEndpoint(DeclarativeMeta):
    def __new__(mcl, name, base, namespace, **kwargs):
        if Endpoint in base:
            if not namespace.get('ConfigEndpoint'):
                namespace['ConfigEndpoint'] = ConfigEndpoint()
            else:
                namespace['ConfigEndpoint'] = ConfigEndpoint(
                    current_config=namespace['ConfigEndpoint'], namespace=namespace
                )
        return super().__new__(mcl, name, base, namespace, **kwargs)
