CONDITIONS = {
    'lt': lambda a, b: a < b,
    'lte': lambda a, b: a <= b,
    'gt': lambda a, b: a > b,
    'gte': lambda a, b: a >= b,
    'equal': lambda a, b: a == b,
}


class UrlParams:
    def __init__(self, model_class, params):
        self.errors = []
        self.params = dict(params).copy()
        self.filter_params = self.params.copy()
        self.order_param = self.filter_params.pop('order', None)
        self.limit_param = self.filter_params.pop('limit', None)
        self.page_param = self.filter_params.pop('page', 1)
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

    @property
    def order_by(self):
        if self.order_param:
            if self.order_param[0] == '-':
                return getattr(self.model_class, self.order_param[1:]).desc()
            return getattr(self.model_class, self.order_param)

    @property
    def columns(self):
        return [c.name for c in self.model_class.__table__.columns]

    def valid_filters(self):
        for filter in self.filter_params:
            cur_filter = filter.split('__')
            if (
                cur_filter[0] not in self.columns
                or len(cur_filter) > 1
                and cur_filter[1] not in ('gte', 'gt', 'lte', 'lt')
            ):
                self.errors.append(f'Filter \'{filter}\' is not valid')

    def valid_order(self):
        if self.order_param:
            order_by = (
                self.order_param if self.order_param[0] != '-' else self.order_param[1:]
            )
            if order_by not in self.columns:
                self.errors.append(f'Order by \'{self.order_param}\' is not valid')

    def valid_number_parameter(self, value, param_name):
        if not value:
            return
        try:
            value = int(value)
        except ValueError:
            self.errors.append(
                f'{param_name} parameter \'{self.limit_param}\' is not correct'
            )
        else:
            return value

    def is_valid(self):
        self.valid_filters()
        self.valid_order()
        self.limit_param = self.valid_number_parameter(self.limit_param, 'Limit')
        self.page_param = self.valid_number_parameter(self.page_param, 'Page')
        if len(self.errors):
            return False
        return True
