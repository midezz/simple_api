from random import randint

import pytest

from simplerestapi import Session


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
        assert resp.json() == model.get_columns_values()

    def assert_post_test(self, data_payload, data_response, model_use, path):
        resp = self.client.post(path, json=data_payload)
        assert resp.status_code == 201
        query = self.session.query(model_use)
        assert query.count() == 1
        item = query.first().get_columns_values()
        data_response['id'] = item['id']
        assert item == data_response
        assert resp.json() == data_response

    def assert_delete_test(self, data, model_use, path):
        model = model_use(**data)
        self.session.add(model)
        self.session.commit()
        resp = self.client.delete(f'{path}/{model.id}')
        assert resp.status_code == 200
        assert resp.json() == model.get_columns_values()
        query = self.session.query(model_use)
        assert query.count() == 0

    def assert_other_methods(self, model_use, path):
        if 'get' not in model_use.ConfigEndpoint.denied_methods:
            self.assert_get_test(get_data(model_use), model_use, path)
            self.rollback_new_session()
        if 'post' not in model_use.ConfigEndpoint.denied_methods:
            data = get_data(model_use)
            self.assert_post_test(data, data, model_use, path)
            self.rollback_new_session()
        if 'delete' not in model_use.ConfigEndpoint.denied_methods:
            self.assert_delete_test(get_data(model_use), model_use, path)
            self.rollback_new_session()
