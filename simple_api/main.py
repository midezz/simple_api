import inspect
from . import api
from .endpoint import Endpoint
from starlette.applications import Starlette
from .router import SimpleApiRouter


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
            handler_class = api.GetAPI
            router = SimpleApiRouter(model, path, handler_class)
            self.routers.append(router)

    def get_handler_class(self, model):
        denied_methods = model.ConfigEndpoint.denied_methods[:]
        if 'post' in denied_methods:
            denied_methods.remove('post')
        denied_methods.sort()
        denied_methods = tuple(denied_methods)
        return api.HANDLER_CLASS.get(denied_methods, api.GetUpdateDeleteAPI)

    def get_models(self, models):
        for _, member in inspect.getmembers(models):
            if inspect.isclass(member) and Endpoint in member.__bases__:
                self.models.append(member)
