from sqlalchemy.ext.declarative import DeclarativeMeta

from .endpoint import Endpoint


class ConfigEndpoint:
    pagination = 100
    denied_methods = []

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
                namespace['ConfigEndpoint'] = ConfigEndpoint
            else:
                for attr, val in ConfigEndpoint.get_attrs().items():
                    if not hasattr(namespace['ConfigEndpoint'], attr):
                        setattr(namespace['ConfigEndpoint'], attr, val)
        return super().__new__(mcl, name, base, namespace, **kwargs)
