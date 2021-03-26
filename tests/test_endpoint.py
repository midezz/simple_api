import pytest

from tests.models import CustomUser


class TestEndpoint:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.model = CustomUser

    @pytest.mark.parametrize(
        'denied_methods, expected',
        (
            (['get', 'post'], 'UpdateDeleteAPI'),
            (['put', 'delete'], 'GetAPI'),
            (['get', 'post', 'delete'], 'UpdateAPI'),
            ([], 'GetUpdateDeleteAPI'),
            (['post', 'delete'], 'GetUpdateAPI'),
            (['put'], 'GetDeleteAPI'),
            (['put', 'get'], 'DeleteAPI'),
        ),
    )
    def test_get_handler_class(self, denied_methods, expected):
        self.model.ConfigEndpoint.denied_methods = denied_methods
        assert self.model.get_handler_class().__name__ == expected

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

    def test_all_other_methonds_not_allowed(self):
        self.model.ConfigEndpoint.denied_methods = ['put', 'delete', 'get']
        assert self.model.get_other_routes() is None

    @pytest.mark.parametrize(
        'denied_methods, expected_class',
        (
            (['get'], 'UpdateDeleteAPI'),
            (['get', 'delete'], 'UpdateAPI'),
            (['delete'], 'GetUpdateAPI'),
            (['put'], 'GetDeleteAPI'),
            (['put', 'delete'], 'GetAPI'),
            (['post'], 'GetUpdateDeleteAPI'),
            ([], 'GetUpdateDeleteAPI'),
        ),
    )
    def test_get_other_routes(self, denied_methods, expected_class):
        self.model.ConfigEndpoint.denied_methods = denied_methods
        router = self.model.get_other_routes()
        assert router.path == '/' + CustomUser.__tablename__ + '/{id}'
        assert router.endpoint.__name__ == expected_class

    def test_get_path(self):
        path = self.model.get_path()
        assert path == '/customuser'

    def test_configured_path(self):
        self.model.ConfigEndpoint.path = '/test_path'
        assert self.model.get_path() == '/test_path'

    def test_get_columns_value(self):
        item = self.model(name='Jon', surname='Dow', age=22)
        values = self.model.get_columns_values(item)
        assert values == {'age': 22, 'id': None, 'name': 'Jon', 'surname': 'Dow'}

    @pytest.mark.parametrize(
        'exclude_fields, expect',
        (
            (['id'], {'age': 22, 'name': 'Jon', 'surname': 'Dow'}),
            (['id', 'age'], {'name': 'Jon', 'surname': 'Dow'}),
            (['id', 'age', 'name', 'surname'], {}),
        ),
    )
    def test_get_columns_values_with_exclude_fields(self, exclude_fields, expect):
        self.model.ConfigEndpoint.exclude_fields = exclude_fields
        item = self.model(name='Jon', surname='Dow', age=22)
        values = self.model.get_columns_values(item)
        assert values == expect
