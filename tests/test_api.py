import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from simple_api import api
from simple_api.router import SimpleApiRouter

from .models import Car

DENIED_METHODS = {
    'CreateAPI': ['get', 'put', 'delete'],
    'ListAPI': ['post', 'put', 'delete'],
    'ListCreateAPI': ['put', 'delete'],
    'GetAPI': ['post', 'put', 'delete'],
    'UpdateAPI': ['post', 'get', 'delete'],
    'DeleteAPI': ['post', 'get', 'put'],
    'GetUpdateDeleteAPI': ['post'],
    'UpdateDeleteAPI': ['post', 'get'],
    'GetDeleteAPI': ['post', 'put'],
    'GetUpdateAPI': ['post', 'delete'],
}


@pytest.mark.usefixtures('db_setup')
class BaseTestAPI:
    @pytest.fixture(autouse=True)
    def setup(self, engine, api_class):
        self.connection = engine.connect()
        api.Session.configure(bind=self.connection)
        self.trans = self.connection.begin()
        self.app = Starlette(routes=[SimpleApiRouter(Car, '/', api_class)])
        self.client = TestClient(self.app)
        self.session = api.Session()
        self.api_class = api_class

    @pytest.fixture(autouse=True)
    def tearDown(self):
        yield
        self.session.close()
        self.trans.rollback()
        self.connection.close()


@pytest.mark.parametrize(
    'api_class',
    (
        api.CreateAPI,
        api.ListAPI,
        api.ListCreateAPI,
        api.GetAPI,
        api.UpdateAPI,
        api.DeleteAPI,
        api.GetUpdateDeleteAPI,
        api.UpdateDeleteAPI,
        api.GetDeleteAPI,
        api.GetUpdateAPI,
    ),
)
class TestDeniedMethods(BaseTestAPI):
    def test_methods(self):
        for method in DENIED_METHODS[self.api_class.__name__]:
            method_call = getattr(self.client, method)
            resp = method_call('/')
            assert resp.status_code == 405
            assert resp.content == b'Method Not Allowed'


@pytest.mark.parametrize('api_class', (api.CreateAPI,))
class TestCreateAPI(BaseTestAPI):
    def test_post(self):
        data = {'name_model': 'test', 'production': 'new test', 'year': 100}
        resp = self.client.post('/', json=data)
        assert resp.status_code == 201
        data['id'] = 1
        query = self.session.query(Car)
        assert query.count() == 1
        item = Car.get_columns_values(query.first())
        assert item == data
