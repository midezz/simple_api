import pytest
from starlette.testclient import TestClient

from simplerestapi import Session
from simplerestapi.main import SimpleApi
from tests import models

from .base import TestBaseApi


@pytest.mark.usefixtures('db_setup')
class TestSimpleApi(TestBaseApi):
    @pytest.fixture(autouse=True)
    def setup(self, engine, db_url_test):
        self.engine = engine
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()
        self.app = SimpleApi(models, db_url_test)
        Session.configure(bind=self.connection)
        self.client = TestClient(self.app.app)
        self.session = Session()

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

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (
                {'name_model': 'test_1', 'production': 'new test 22', 'year': 200},
                models.Car,
                '/new_car_path',
            ),
            (
                {'name': 'Ivan_1', 'surname': 'Petrov_1', 'age': 35},
                models.CustomUser,
                '/new_user_path',
            ),
        ),
    )
    def test_post_custom_path(self, data, model_use, path):
        self.assert_post_test(data, model_use, path)

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
        self.assert_other_methods(models.CustomUser, '/customuser')
        self.assert_other_methods(models.Car, '/car')
