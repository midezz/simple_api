from sqlalchemy.ext.declarative import declared_attr

from .api import HANDLER_CLASS, HANDLER_CLASS_LISTCREATE, GetUpdateDeleteAPI
from .router import SimpleApiRouter


CONDITIONS = {
    'lt': lambda a, b: a < b,
    'lte': lambda a, b: a <= b,
    'gt': lambda a, b: a > b,
    'gte': lambda a, b: a >= b,
    'equal': lambda a, b: a == b
}


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

    @classmethod
    def construct_filters(cls, params):
        filters = []
        for param, value in params.items():
            conditions = param.split('__')
            if len(conditions) > 1:
                criterion = CONDITIONS.get(conditions[1])(getattr(cls, conditions[0]), value)
                filters.append(criterion)
            else:
                criterion = CONDITIONS.get('equal')(getattr(cls, conditions[0]), value)
                filters.append(criterion)
        return filters

    @classmethod
    def valid_filters(cls, params):
        columns = [c.name for c in cls.__table__.columns]
        for filter in params:
            cur_filter = filter.split('__')
            if cur_filter[0] not in columns or len(cur_filter) > 1 and cur_filter[1] not in ('gte', 'gt', 'lte', 'lt'):
                return {'error': f'Filter \'{filter}\' is not valid'}
        return {'valid': True}
