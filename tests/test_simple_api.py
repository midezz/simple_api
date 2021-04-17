import pytest

from simple_api import Session
from simple_api.main import SimpleApi

from starlette.testclient import TestClient

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


class TestBaseGet(TestSimpleApi):
    def test_get(self):
        data = {'name_model': 'test', 'production': 'new test', 'year': 100}
        model = models.Car(**data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.get(f'car/{model.id}')
        assert resp.status_code == 200
        assert resp.json() == models.Car.get_columns_values(model)
