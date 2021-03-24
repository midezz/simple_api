import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from simple_api import Session, api
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
    def setup(self, engine, api_class, path):
        self.connection = engine.connect()
        Session.configure(bind=self.connection)
        self.trans = self.connection.begin()
        self.app = Starlette(routes=[SimpleApiRouter(Car, path, api_class)])
        self.client = TestClient(self.app)
        self.session = Session()
        self.api_class = api_class

    @pytest.fixture(autouse=True)
    def tearDown(self):
        yield
        self.session.close()
        self.trans.rollback()
        self.connection.close()


@pytest.mark.parametrize(
    'api_class, path',
    (
        (api.CreateAPI, '/'),
        (api.ListAPI, '/'),
        (api.ListCreateAPI, '/'),
        (api.GetAPI, '/'),
        (api.UpdateAPI, '/'),
        (api.DeleteAPI, '/'),
        (api.GetUpdateDeleteAPI, '/'),
        (api.UpdateDeleteAPI, '/'),
        (api.GetDeleteAPI, '/'),
        (api.GetUpdateAPI, '/'),
    ),
)
class TestDeniedMethods(BaseTestAPI):
    def test_methods(self):
        for method in DENIED_METHODS[self.api_class.__name__]:
            method_call = getattr(self.client, method)
            resp = method_call('/')
            assert resp.status_code == 405
            assert resp.content == b'Method Not Allowed'


@pytest.mark.parametrize('api_class, path', ((api.CreateAPI, '/'),))
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
        assert resp.json() == data

    @pytest.mark.parametrize(
        'data',
        (
            {'name_model': 'test', 'production': 'new test', 'year': 'a'},
            {
                'name_model': 'test',
                'production': 'new test',
                'year': 100,
                'not_exist_field': 'test',
            },
        ),
    )
    def test_bad_request(self, data):
        data = {'name_model': 'test', 'production': 'new test', 'year': 'a'}
        resp = self.client.post('/', json=data)
        assert resp.status_code == 400
        assert resp.json() == {'error': True}
        query = self.session.query(Car)
        assert query.count() == 0


@pytest.mark.parametrize('api_class, path', ((api.GetAPI, '/{id}'),))
class TestGetAPI(BaseTestAPI):
    def test_get(self):
        data = {'name_model': 'test', 'production': 'new test', 'year': 100}
        model = Car(**data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.get(f'/{model.id}')
        assert resp.status_code == 200
        assert resp.json() == Car.get_columns_values(model)

    def test_get_not_found(self):
        data = {'name_model': 'test', 'production': 'new test', 'year': 100}
        model = Car(**data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.get(f'/{model.id + 1}')
        assert resp.status_code == 404


@pytest.mark.parametrize('api_class, path', ((api.DeleteAPI, '/{id}'),))
class TestDeleteAPI(BaseTestAPI):
    def test_delete(self):
        data = {'name_model': 'test', 'production': 'new test', 'year': 100}
        model = Car(**data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.delete(f'/{model.id}')
        assert resp.status_code == 200
        assert resp.json() == Car.get_columns_values(model)
        query = self.session.query(Car)
        assert query.count() == 0

    def test_delete_not_found(self):
        data = {'name_model': 'test', 'production': 'new test', 'year': 100}
        model = Car(**data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.delete(f'/{model.id + 1}')
        assert resp.status_code == 404
