import pytest

from tests.models import Car, CustomUser


class TestEndpoint:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.model = CustomUser

    def test_get_listcreate_routes_is_none(self):
        self.model.ConfigEndpoint.denied_methods = ['post']
        self.model.ConfigEndpoint.pagination = 0
        assert self.model.get_listcreate_routes() is None

    @pytest.mark.parametrize(
        'denied_methods, pagination, expected_class',
        (
            (['post'], 100, 'ListAPI'),
            ([], 100, 'ListCreateAPI'),
            ([], 0, 'CreateAPI'),
        ),
    )
    def test_get_listcreate_routes(self, denied_methods, pagination, expected_class):
        self.model.ConfigEndpoint.denied_methods = denied_methods
        self.model.ConfigEndpoint.pagination = pagination
        router = self.model.get_listcreate_routes()
        assert router.path == '/' + CustomUser.__tablename__
        assert router.endpoint.__name__ == expected_class

    def test_get_other_routes(self):
        router = self.model.get_other_routes()
        assert router.path == '/' + CustomUser.__tablename__ + '/{id}'
        assert router.endpoint.__name__ == 'GetUpdateDeleteAPI'

    def test_get_path(self):
        path = self.model.get_path()
        assert path == '/customuser'

    def test_configured_path(self):
        self.model._config_endpoint(path='/test_path')
        assert self.model.get_path() == '/test_path'

    @pytest.mark.parametrize(
        'join_related, expected',
        (
            ([], {'age': 22, 'id': None, 'name': 'Jon', 'surname': 'Dow'}),
            (['car'], {'age': 22, 'id': None, 'name': 'Jon', 'surname': 'Dow', 'car': []}),
        ),
    )
    def test_get_columns_value(self, join_related, expected):
        self.model._config_endpoint(join_related=join_related)
        item = self.model(name='Jon', surname='Dow', age=22)
        values = item.get_columns_values()
        assert values == expected

    def test_get_columns_value_none_foreign_key(self):
        Car._config_endpoint(join_related=['customuser'])
        item = Car(name_model='Car 1', production='Production 1', year=2015)
        values = item.get_columns_values()
        expected = {
            'id': None,
            'name_model': 'Car 1',
            'production': 'Production 1',
            'year': 2015,
            'customuser_id': None,
            'customuser': None,
        }
        assert values == expected

    def test_get_joins(self):
        self.model._config_endpoint(join_related=['car'])
        joins = self.model.get_joins()
        assert joins == [self.model.car]

    @pytest.mark.parametrize(
        'join_next_level, expected',
        (
            (
                True,
                {
                    'id': None,
                    'name': 'Jon',
                    'surname': 'Dow',
                    'age': 22,
                    'car': [
                        {
                            'id': None,
                            'name_model': 'Car 1',
                            'production': 'Production 1',
                            'year': 2015,
                            'customuser_id': None,
                        },
                        {
                            'id': None,
                            'name_model': 'Car 2',
                            'production': 'Production 2',
                            'year': 2018,
                            'customuser_id': None,
                        },
                    ],
                },
            ),
            (
                False,
                {
                    'id': None,
                    'name': 'Jon',
                    'surname': 'Dow',
                    'age': 22,
                },
            ),
        ),
    )
    def test_get_columns_value_with_relative(self, join_next_level, expected):
        item = self.model(name='Jon', surname='Dow', age=22)
        item.car = [
            Car(name_model='Car 1', production='Production 1', year=2015),
            Car(name_model='Car 2', production='Production 2', year=2018),
        ]
        item._config_endpoint(join_related=['car'], exclude_fields=[])
        values = item.get_columns_values(next_relative_level=join_next_level)
        assert values == expected

    @pytest.mark.parametrize(
        'exclude_fields, expect',
        (
            (['id'], {'age': 22, 'name': 'Jon', 'surname': 'Dow'}),
            (['id', 'age'], {'name': 'Jon', 'surname': 'Dow'}),
            (['id', 'age', 'name', 'surname'], {}),
        ),
    )
    def test_get_columns_values_with_exclude_fields(self, exclude_fields, expect):
        self.model._config_endpoint(exclude_fields=exclude_fields)
        item = self.model(name='Jon', surname='Dow', age=22)
        values = item.get_columns_values()
        assert values == expect
