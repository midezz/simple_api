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
        assert resp.json() == {'errors': ['Bad request']}
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


@pytest.mark.parametrize('api_class, path', ((api.ListAPI, '/'),))
class TestListAPI(BaseTestAPI):
    def test_list(self):
        models = [
            Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n})
            for n in range(30)
        ]
        self.session.add_all(models)
        self.session.commit()
        resp = self.client.get('/')
        assert resp.status_code == 200
        result = resp.json()
        assert len(result) == len(models)
        except_result = [Car.get_columns_values(model) for model in models]
        assert result == except_result

    def test_empty_list(self):
        resp = self.client.get('/')
        assert resp.status_code == 200
        result = resp.json()
        assert len(result) == 0

    @pytest.mark.parametrize(
        'filters, expect_ids',
        (
            ({'year': 2014}, (31,)),
            ({'year__gt': 2014}, (30, 32, 33)),
            ({'year__lt': 1}, (0,)),
            ({'year__gte': 2021}, (30, 32, 33)),
            ({'year__gt': 2021, 'production': 'Porsche'}, (33,)),
            ({'year__lte': 1}, (0, 1)),
            ({'year__gt': 2014, 'year__lt': 2025}, (30, 32)),
            ({'production': 'Toyota'}, ()),
        ),
    )
    def test_filter(self, filters, expect_ids):
        models = [
            Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n})
            for n in range(30)
        ]
        models.append(Car(name_model='Model 3', production='Tesla', year=2021))
        models.append(Car(name_model='Octavia', production='Skoda', year=2014))
        models.append(Car(name_model='Boxter', production='Porsche', year=2021))
        models.append(Car(name_model='911', production='Porsche', year=2025))
        self.session.add_all(models)
        self.session.commit()
        resp = self.client.get('/', params=filters)
        assert resp.status_code == 200
        result = resp.json()
        expect = [Car.get_columns_values(models[i]) for i in expect_ids]
        assert result == expect

    @pytest.mark.parametrize(
        'order, expect_ids',
        (
            ({'order': 'year'}, (2, 1, 0)),
            ({'order': 'id'}, (0, 1, 2)),
            ({'order': '-id'}, (2, 1, 0)),
        ),
    )
    def test_order(self, order, expect_ids):
        models = [
            Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n})
            for n in range(3, 0, -1)
        ]
        self.session.add_all(models)
        self.session.commit()
        resp = self.client.get('/', params=order)
        assert resp.status_code == 200
        result = resp.json()
        expect = [Car.get_columns_values(models[i]) for i in expect_ids]
        assert result == expect

    def test_noncorrect_request(self):
        models = [
            Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n})
            for n in range(10)
        ]
        self.session.add_all(models)
        self.session.commit()
        resp = self.client.get('/', params={'test': 'test'})
        assert resp.status_code == 400
        result = resp.json()
        assert result == {'errors': ["Filter 'test' is not valid"]}
