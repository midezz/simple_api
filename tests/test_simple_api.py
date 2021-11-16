import pytest
from starlette.testclient import TestClient

from simplerestapi import Session
from simplerestapi.main import SimpleApi
from tests import models

from .base import TestBaseApi, get_data


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
    @pytest.fixture(autouse=True)
    def pre_setup(self):
        models.Car._config_endpoint(exclude_fields=['customuser_id'])

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (get_data(models.Car), models.Car, '/car'),
            (get_data(models.CustomUser), models.CustomUser, '/customuser'),
        ),
    )
    def test_get(self, data, model_use, path):
        self.assert_get_test(data, model_use, path)

    def test_get_with_join_related(self):
        cars_data = [get_data(models.Car) for _ in range(3)]
        cars = [models.Car(**data) for data in cars_data]
        user_data = get_data(models.CustomUser)
        user = models.CustomUser(**user_data)
        user.car = cars
        self.session.add(user)
        self.session.add(models.Car(**get_data(models.Car)))
        self.session.commit()
        models.Car._config_endpoint(join_related=['customuser'], exclude_fields=[])
        models.CustomUser._config_endpoint(join_related=['car'])
        resp = self.client.get(f'/customuser/{user.id}')
        expected = {
            'id': user.id,
            **user_data,
            'car': [{'id': c.id, **c_data, 'customuser_id': user.id} for c, c_data in zip(cars, cars_data)],
        }
        assert resp.status_code == 200
        assert resp.json() == expected
        for car, car_data in zip(cars, cars_data):
            resp = self.client.get(f'/car/{car.id}')
            expected = {'id': car.id, **car_data, 'customuser_id': user.id, 'customuser': {'id': user.id, **user_data}}
            assert resp.status_code == 200
            assert resp.json() == expected

    def test_get_with_join_none_related(self):
        car_data = get_data(models.Car)
        user_data = get_data(models.CustomUser)
        car = models.Car(**car_data)
        user = models.CustomUser(**user_data)
        self.session.add(car)
        self.session.add(user)
        self.session.commit()
        models.Car._config_endpoint(join_related=['customuser'], exclude_fields=[])
        models.CustomUser._config_endpoint(join_related=['car'])
        resp = self.client.get(f'/customuser/{user.id}')
        expected = {'id': user.id, **user_data, 'car': []}
        assert resp.status_code == 200
        assert resp.json() == expected
        resp = self.client.get(f'/car/{car.id}')
        expected = {'id': car.id, **car_data, 'customuser_id': None, 'customuser': None}
        assert resp.status_code == 200
        assert resp.json() == expected

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (get_data(models.Car), models.Car, '/car'),
            (get_data(models.CustomUser), models.CustomUser, '/customuser'),
        ),
    )
    def test_post(self, data, model_use, path):
        self.assert_post_test(data, model_use, path)

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (get_data(models.Car), models.Car, '/car'),
            (get_data(models.CustomUser), models.CustomUser, '/customuser'),
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
        models.Car._config_endpoint(path='/new_car_path', exclude_fields=['customuser_id'])
        models.CustomUser._config_endpoint(path='/new_user_path')

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (get_data(models.Car), models.Car, '/new_car_path'),
            (get_data(models.CustomUser), models.CustomUser, '/new_user_path'),
        ),
    )
    def test_get_custom_path(self, data, model_use, path):
        self.assert_get_test(data, model_use, path)

    @pytest.mark.parametrize(
        'data, model_use, path',
        (
            (get_data(models.Car), models.Car, '/new_car_path'),
            (get_data(models.CustomUser), models.CustomUser, '/new_user_path'),
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
        models.Car._config_endpoint(denied_methods=[method], exclude_fields=['customuser_id'])

    def test_denied_method(self):
        method = getattr(self.client, self.methond)
        resp = method(self.path)
        assert resp.status_code == 405
        self.assert_other_methods(models.CustomUser, '/customuser')
        self.assert_other_methods(models.Car, '/car')
