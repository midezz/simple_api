import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from simplerestapi import Session, api
from simplerestapi.router import SimpleApiRouter

from .base import TestBaseApi
from .models import Car, CustomUser


@pytest.mark.usefixtures('db_setup')
class BaseTestAPIClass(TestBaseApi):
    api_class = api.GetUpdateDeleteAPI
    denied_methods = []
    path = '/'

    @pytest.fixture(autouse=True)
    def setup(self, engine):
        self.connection = engine.connect()
        Session.configure(bind=self.connection)
        self.trans = self.connection.begin()
        Car._config_endpoint(denied_methods=self.denied_methods)
        self.app = Starlette(routes=[SimpleApiRouter(Car, self.path, self.api_class)])
        self.client = TestClient(self.app)
        self.session = Session()


@pytest.mark.parametrize(
    'api_class, denied_methods',
    (
        (api.CreateAPI, ['get', 'put', 'delete', 'patch']),
        (api.ListAPI, ['post', 'put', 'delete', 'patch']),
        (api.ListCreateAPI, ['put', 'delete', 'patch']),
        (api.GetUpdateDeleteAPI, ['post']),
        (api.GetUpdateDeleteAPI, ['get']),
        (api.GetUpdateDeleteAPI, ['put']),
        (api.GetUpdateDeleteAPI, ['delete']),
        (api.GetUpdateDeleteAPI, ['patch']),
    ),
)
class TestDeniedMethods(BaseTestAPIClass):
    @pytest.fixture(autouse=True)
    def pre_setup(self, api_class, denied_methods):
        self.api_class = api_class
        self.denied_methods = denied_methods

    def test_methods(self):
        for method in self.denied_methods:
            method_call = getattr(self.client, method)
            resp = method_call('/')
            assert resp.status_code == 405
            assert resp.content == b'Method Not Allowed'


class TestCreateAPI(BaseTestAPIClass):
    api_class = api.CreateAPI

    def test_post(self):
        data_payload = {'name_model': 'test', 'production': 'new test', 'year': 100}
        data_resp = {'name_model': 'test', 'production': 'new test', 'year': 100, 'customuser_id': None}
        self.assert_post_test(data_payload, data_resp, Car, '/')

    @pytest.mark.parametrize(
        'data',
        (
            {'name_model': 'test', 'production': 'new test', 'year': 'a'},
            {'name_model': 'test'},
            {
                'name_model': 'test',
                'production': 'new test',
                'year': 100,
                'not_exist_field': 'test',
            },
        ),
    )
    def test_bad_request(self, data):
        resp = self.client.post('/', json=data)
        assert resp.status_code == 400
        assert resp.json() == {'errors': ['Bad request']}
        query = self.session.query(Car)
        assert query.count() == 0


class TestGetUpdateDeleteAPI(BaseTestAPIClass):
    path = '/{id}'
    data = {'name_model': 'test', 'production': 'new test', 'year': 100}

    def test_get(self):
        Car._config_endpoint(exclude_fields=['customuser_id'])
        self.assert_get_test(self.data, Car, '')

    def test_get_with_join_related(self):
        Car._config_endpoint(join_related=['customuser'])
        car = Car(**self.data)
        user = CustomUser(name='John', surname='Dow', age=18)
        car.customuser = user
        self.session.add(car)
        self.session.commit()
        resp = self.client.get(f'/{car.id}')
        assert resp.status_code == 200
        expected = {
            'id': car.id,
            'name_model': 'test',
            'production': 'new test',
            'year': 100,
            'customuser_id': user.id,
            'customuser': {'id': user.id, 'name': 'John', 'surname': 'Dow', 'age': 18},
        }
        assert resp.json() == expected

    def test_get_not_found(self):
        model = Car(**self.data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.get(f'/{model.id + 1}')
        assert resp.status_code == 404

    def test_delete(self):
        self.assert_delete_test(self.data, Car, '')

    def test_delete_not_found(self):
        model = Car(**self.data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.delete(f'/{model.id + 1}')
        assert resp.status_code == 404

    @pytest.mark.parametrize('method', ('put', 'patch'))
    def test_update(self, method):
        data = {'name_model': 'Model 3', 'production': 'Tesla', 'year': 2022}
        model = Car(**data)
        self.session.add(model)
        self.session.commit()
        request_method = getattr(self.client, method)
        resp = request_method(f'/{model.id}', json={'year': 2020, 'name_model': 'Model 1'})
        self.session.refresh(model)
        assert resp.status_code == 200
        assert resp.json() == {
            'id': str(model.id),
            'year': 2020,
            'name_model': 'Model 1',
        }
        assert model.year == 2020
        assert model.name_model == 'Model 1'
        assert model.production == 'Tesla'

    @pytest.mark.parametrize('method', ('put', 'patch'))
    @pytest.mark.parametrize(
        'id, status_code, error, payload',
        (
            (0, 400, 'Bad request', {'year': 2020, 'test_name_model': 'Model 1'}),
            (1, 404, 'Not found', {'year': 2020, 'name_model': 'Model 1'}),
        ),
    )
    def test_update_bad_request(self, method, id, status_code, error, payload):
        data = {'name_model': 'Model 3', 'production': 'Tesla', 'year': 2022}
        model = Car(**data)
        self.session.add(model)
        self.session.commit()
        request_method = getattr(self.client, method)
        resp = request_method(f'/{model.id+id}', json=payload)
        self.session.refresh(model)
        assert resp.status_code == status_code
        assert resp.json().get('errors') == [error]
        assert model.year == 2022
        assert model.name_model == 'Model 3'
        assert model.production == 'Tesla'


class TestListAPI(BaseTestAPIClass):
    api_class = api.ListAPI

    def test_list(self):
        models = [Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n}) for n in range(30)]
        self.session.add_all(models)
        self.session.commit()
        resp = self.client.get('/')
        assert resp.status_code == 200
        result = resp.json()
        assert len(result) == len(models)
        except_result = [model.get_columns_values() for model in models]
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
        models = [Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n}) for n in range(30)]
        models.append(Car(name_model='Model 3', production='Tesla', year=2021))
        models.append(Car(name_model='Octavia', production='Skoda', year=2014))
        models.append(Car(name_model='Boxter', production='Porsche', year=2021))
        models.append(Car(name_model='911', production='Porsche', year=2025))
        self.session.add_all(models)
        self.session.commit()
        resp = self.client.get('/', params=filters)
        assert resp.status_code == 200
        result = resp.json()
        expect = [models[i].get_columns_values() for i in expect_ids]
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
        models = [Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n}) for n in range(3, 0, -1)]
        self.session.add_all(models)
        self.session.commit()
        resp = self.client.get('/', params=order)
        assert resp.status_code == 200
        result = resp.json()
        expect = [models[i].get_columns_values() for i in expect_ids]
        assert result == expect

    @pytest.mark.parametrize(
        'limit, start, end',
        (
            ({'limit': 5}, 0, 5),
            ({'page': 2}, 100, 200),
            ({'page': 2, 'limit': 5}, 0, 0),
            ({'page': 2, 'limit': 133}, 100, 133),
            ({'page': 3, 'limit': 133}, 0, 0),
            ({'page': 2, 'limit': 320}, 100, 200),
            ({'page': 1, 'limit': 15}, 0, 15),
        ),
    )
    def test_limit_page(self, limit, start, end):
        models = [Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n}) for n in range(330)]
        self.session.add_all(models)
        self.session.commit()
        limit.update({'order': 'id'})
        resp = self.client.get('/', params=limit)
        assert resp.status_code == 200
        result = resp.json()
        expect = [models[i].get_columns_values() for i in range(start, end)]
        assert result == expect

    def test_noncorrect_request(self):
        models = [Car(**{'name_model': f'test{n}', 'production': f'new test{n}', 'year': n}) for n in range(10)]
        self.session.add_all(models)
        self.session.commit()
        resp = self.client.get('/', params={'test': 'test'})
        assert resp.status_code == 400
        result = resp.json()
        assert result == {'errors': ["Filter 'test' is not valid"]}
