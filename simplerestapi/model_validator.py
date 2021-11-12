from pydantic import BaseModel, validator


class BaseConfigEndpoint(BaseModel):
    pagination: int = 100
    denied_methods: list = []
    path: str = None
    exclude_fields: list = []

    @validator('denied_methods')
    def denied_methods_validate(cls, v):
        correct_methods = {'get', 'post', 'delete', 'put', 'patch'}
        if len(v) > 0 and set(v) - correct_methods:
            raise ValueError('methods must be from list (\'get\', \'post\', \'delete\', \'put\', \'patch\')')

    @validator('pagination')
    def pagination_validate(cls, v):
        if v < 0:
            raise ValueError('value must be above or equal 0')


class ModelValidator:
    def __init__(self, model):
        self.model = model
        self.errors = []
        self.validate_config_endpoint(model)

    def validate_config_endpoint(self, model):
        base_config_properties = set(BaseConfigEndpoint.schema()['properties'])
        model_config_properties = {key for key in model.ConfigEndpoint.__dict__ if not key.startswith('__')}
        config_properties = {key: getattr(model.ConfigEndpoint, key) for key in base_config_properties}
        if len(model_config_properties - base_config_properties) > 0:
            msg = '\'{0}\': not support parameters'
            self.add_error(msg.format(', '.join(model_config_properties - base_config_properties)))
        try:
            _ = BaseConfigEndpoint(**config_properties)
        except Exception as e:
            for error in e.errors():
                error_msg = f'\'{" ".join(error["loc"])}\': {error["msg"]}'
                self.add_error(error_msg)

    def add_error(self, error_msg):
        self.errors.append(f'Model \'{self.model.__name__}\' has incorrect ConfigEndpoint parameter {error_msg}')
