CONDITIONS = {
    'lt': lambda a, b: a < b,
    'lte': lambda a, b: a <= b,
    'gt': lambda a, b: a > b,
    'gte': lambda a, b: a >= b,
    'equal': lambda a, b: a == b,
}


class UrlParams:
    error = None

    def __init__(self, model_class, params):
        self.params = dict(params).copy()
        self.filter_params = self.params.copy()
        self.order_params = self.filter_params.pop('order', None)
        self.model_class = model_class

    @property
    def filters(self):
        res_filters = []
        for param, value in self.filter_params.items():
            conditions = param.split('__')
            if len(conditions) > 1:
                criterion = CONDITIONS.get(conditions[1])(
                    getattr(self.model_class, conditions[0]), value
                )
                res_filters.append(criterion)
            else:
                criterion = CONDITIONS.get('equal')(
                    getattr(self.model_class, conditions[0]), value
                )
                res_filters.append(criterion)
        return res_filters

    def valid_filters(self):
        columns = [c.name for c in self.model_class.__table__.columns]
        for filter in self.params:
            cur_filter = filter.split('__')
            if (
                cur_filter[0] not in columns
                or len(cur_filter) > 1
                and cur_filter[1] not in ('gte', 'gt', 'lte', 'lt')
            ):
                self.error = f'Filter \'{filter}\' is not valid'
                return False
        return True

    def is_valid(self):
        if not self.valid_filters():
            return False
        return True
