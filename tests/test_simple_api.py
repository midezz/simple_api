import pytest
from starlette.testclient import TestClient

from simple_api import Session
from simple_api.main import SimpleApi
from tests import models


@pytest.mark.usefixtures('db_setup')
class TestSimpleApi:
    @pytest.fixture(autouse=True)
    def setup(self, engine, db_url_test):
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.app = SimpleApi(models, db_url_test)
        Session.configure(bind=self.connection)
        self.client = TestClient(self.app.app)
        self.session = Session()

    @pytest.fixture(autouse=True)
    def tearDown(self):
        yield
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def assert_get_test(self, data, model_use, path):
        model = model_use(**data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.get(f'{path}/{model.id}')
        assert resp.status_code == 200
        assert resp.json() == model_use.get_columns_values(model)

    def assert_post_test(self, data, model_use, path):
        resp = self.client.post(path, json=data)
        assert resp.status_code == 201
        query = self.session.query(model_use)
        assert query.count() == 1
        item = model_use.get_columns_values(query.first())
        data['id'] = item['id']
        assert item == data
        assert resp.json() == data

    def assert_delete_test(self, data, model_use, path):
        model = model_use(**data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.delete(f'{path}/{model.id}')
        assert resp.status_code == 200
        assert resp.json() == model_use.get_columns_values(model)
        query = self.session.query(model_use)
        assert query.count() == 0

    def assert_not_found(self, resp):
        assert resp.content == b'Not Found'
        assert resp.status_code == 404


class TestBase(TestSimpleApi):
    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (
                {'name_model': 'test', 'production': 'new test', 'year': 100},
                models.Car,
                '/car',
            ),
            (
                {'name': 'Ivan', 'surname': 'Petrov', 'age': 30},
                models.CustomUser,
                '/customuser',
            ),
        ),
    )
    def test_get(self, data, model_use, path):
        self.assert_get_test(data, model_use, path)

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (
                {'name_model': 'Model 3', 'production': 'Tesla', 'year': 1},
                models.Car,
                '/car',
            ),
            (
                {'name': 'Petr', 'surname': 'Ivanov', 'age': 29},
                models.CustomUser,
                '/customuser',
            ),
        ),
    )
    def test_post(self, data, model_use, path):
        self.assert_post_test(data, model_use, path)

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (
                {'name_model': 'Model 3', 'production': 'Tesla', 'year': 1},
                models.Car,
                '/car',
            ),
            (
                {'name': 'Petr', 'surname': 'Ivanov', 'age': 29},
                models.CustomUser,
                '/customuser',
            ),
        ),
    )
    def test_delete(self, data, model_use, path):
        self.assert_delete_test(data, model_use, path)

    def test_not_found_path(self):
        resp = self.client.get('/not_exists_path')
        self.assert_not_found(resp)


class TestCustomizePath(TestSimpleApi):
    @pytest.fixture(autouse=True)
    def pre_setup(self):
        models.Car.ConfigEndpoint.path = '/new_car_path'
        models.CustomUser.ConfigEndpoint.path = '/new_user_path'

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (
                {'name_model': 'test', 'production': 'new test', 'year': 100},
                models.Car,
                '/new_car_path',
            ),
            (
                {'name': 'Ivan', 'surname': 'Petrov', 'age': 30},
                models.CustomUser,
                '/new_user_path',
            ),
        ),
    )
    def test_get_custom_path(self, data, model_use, path):
        self.assert_get_test(data, model_use, path)

    @pytest.mark.parametrize('path', ('/car', '/customuser'))
    def test_old_path(self, path):
        resp = self.client.get(path)
        self.assert_not_found(resp)


@pytest.mark.parametrize(
    'method, path',
    (
        ('post', '/car'),
        ('get', '/car/1'),
        ('delete', '/car/1'),
        ('put', '/car/1'),
        ('patch', '/car/1'),
    ),
)
class TestDeniedMethods(TestSimpleApi):
    @pytest.fixture(autouse=True)
    def pre_setup(self, method, path):
        self.methond = method
        self.path = path
        models.Car.ConfigEndpoint.denied_methods = [method]

    def test_denied_method(self):
        method = getattr(self.client, self.methond)
        resp = method(self.path)
        assert resp.status_code == 405
