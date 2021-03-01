from re import S
from sqlalchemy.ext.declarative import declared_attr
import inspect
from starlette.routing import Route
from .api import RetrieveView
from starlette.applications import Starlette
from .router import SimpleApiRouter


class Endpoint:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    class ConfigEndpoint:
        pegination = 100
        denied_methods = []


class SimpleApi:
    models = []
    routers = []

    def __init__(self, models):
        self.get_models(models)
        self.get_routes()
        self.app = Starlette(debug=True, routes=self.routers)

    def get_routes(self):
        for model in self.models:
            path = '/' + model.__tablename__
            handler_class = RetrieveView
            router = SimpleApiRouter(model, path, handler_class)
            self.routers.append(router)

    def get_models(self, models):
        for _, member in inspect.getmembers(models):
            if inspect.isclass(member) and Endpoint in member.__bases__:
                self.models.append(member)
