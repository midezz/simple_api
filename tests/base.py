from random import randint

import pytest

from simple_api import Session


def get_data(model_use):
    data = {
        'Car': {
            'name_model': f'test_{randint(1, 50)}',
            'production': f'new test_{randint(1, 50)}',
            'year': randint(1, 100),
        },
        'CustomUser': {
            'name': f'Ivan_{randint(1, 50)}',
            'surname': f'Petrov_{randint(1, 50)}',
            'age': randint(1, 50),
        },
    }
    return data.get(model_use.__name__)


class TestBaseApi:
    @pytest.fixture(autouse=True)
    def tearDown(self):
        yield
        self.session.close()
        self.trans.rollback()
        self.connection.close()

    def rollback_new_session(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()
        Session.configure(bind=self.connection)
        self.session = Session()

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

    def assert_other_methods(self, model_use, path):
        if 'get' not in model_use.ConfigEndpoint.denied_methods:
            self.assert_get_test(get_data(model_use), model_use, path)
            self.rollback_new_session()
        if 'post' not in model_use.ConfigEndpoint.denied_methods:
            self.assert_post_test(get_data(model_use), model_use, path)
            self.rollback_new_session()
        if 'delete' not in model_use.ConfigEndpoint.denied_methods:
            self.assert_delete_test(get_data(model_use), model_use, path)
            self.rollback_new_session()
