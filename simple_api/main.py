import inspect

from starlette.applications import Starlette

from .endpoint import Endpoint


class SimpleApi:
    models = []
    routes = []

    def __init__(self, models):
        self.get_models(models)
        self.get_routes()
        self.app = Starlette(debug=True, routes=self.routes)

    def get_routes(self):
        for model in self.models:
            listcreate_routes = model.get_listcreate_routes()
            if listcreate_routes:
                self.routes.append(listcreate_routes)
            other_routes = model.get_other_routes()
            if other_routes:
                self.routes.append(other_routes)

    def get_models(self, models):
        for _, member in inspect.getmembers(models):
            if inspect.isclass(member) and Endpoint in member.__bases__:
                self.models.append(member)
