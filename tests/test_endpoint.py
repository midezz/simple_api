import pytest
from sqlalchemy.orm import sessionmaker

from tests.models import CustomUser

Session = sessionmaker()


class TestEndpoint:
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
        )
    )
    def test_get_handler_class(self, denied_methods, expected):
        model = CustomUser
        model.ConfigEndpoint.denied_methods = denied_methods
        assert model.get_handler_class().__name__ == expected

    def test_get_listcreate_routes_is_none(self):
        model = CustomUser
        model.ConfigEndpoint.denied_methods = ['post']
        model.ConfigEndpoint.pagination = 0
        assert model.get_listcreate_routes(Session) is None

    @pytest.mark.parametrize(
        'denied_methods, pagination, expected_class',
        (
            (['post'], 100, 'ListAPI'),
            ([], 100, 'ListCreateAPI'),
            ([], 0, 'CreateAPI'),
        )
    )
    def test_get_listcreate_routes(self, denied_methods, pagination, expected_class):
        model = CustomUser
        model.ConfigEndpoint.denied_methods = denied_methods
        model.ConfigEndpoint.pagination = pagination
        router = model.get_listcreate_routes(Session)
        assert router.path == '/' + CustomUser.__tablename__
        assert router.endpoint.__name__ == expected_class

    def test_all_other_methonds_not_allowed(self):
        model = CustomUser
        model.ConfigEndpoint.denied_methods = ['put', 'delete', 'get']
        assert model.get_other_routes(Session) is None

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

        )
    )
    def test_get_other_routes(self, denied_methods, expected_class):
        model = CustomUser
        model.ConfigEndpoint.denied_methods = denied_methods
        router = model.get_other_routes(Session)
        assert router.path == '/' + CustomUser.__tablename__ + '/{id}'
        assert router.endpoint.__name__ == expected_class

    @pytest.mark.parametrize(
        'filters, expected',
        (
            ({'name': 'test'}, {'valid': True}),
            ({'name__gte': 'test'}, {'valid': True}),
            ({'name__lte': 'test'}, {'valid': True}),
            ({'name__gt': 'test'}, {'valid': True}),
            ({'name__lt': 'test'}, {'valid': True}),
            ({'bla': 'test'}, {'error': 'Filter \'bla\' is not valid'}),
            ({'name__bla': 'test'}, {'error': 'Filter \'name__bla\' is not valid'}),
        )
    )
    def test_validate_filters(self, filters, expected):
        assert CustomUser.valid_filters(filters) == expected
