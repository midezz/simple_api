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
            raise ValueError(
                'methods must be from list (\'get\', \'post\', \'delete\', \'put\', \'patch\')'
            )


class ModelValidator:
    def __init__(self, model):
        self.model = model
        self.errors = []
        self.validate_config_endpoint(model)

    def validate_config_endpoint(self, model):
        config_properties = {
            key: getattr(model.ConfigEndpoint, key)
            for key in BaseConfigEndpoint.schema()['properties']
        }
        try:
            _ = BaseConfigEndpoint(**config_properties)
        except Exception as e:
            for error in e.errors():
                error_msg = f'\'{" ".join(error["loc"])}\': {error["msg"]}'
                self.errors.append(
                    f'Model \'{self.model.__name__}\' has incorrect ConfigEndpoint parameter {error_msg}'
                )
