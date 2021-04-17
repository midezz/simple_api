import inspect

from sqlalchemy import create_engine
from starlette.applications import Starlette

from . import Session
from .endpoint import Endpoint


class SimpleApi:
    def __init__(self, models, db, debug=True):
        self.models = []
        self.routes = []
        self.get_models(models)
        self.construct_routes()
        self.engine = create_engine(db)
        Session.configure(bind=self.engine)
        self.app = Starlette(debug=debug, routes=self.routes)

    def construct_routes(self):
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
