from typing import List, Union

from pydantic import BaseModel, validator


class BaseConfigEndpoint(BaseModel):
    pagination: int = 100
    denied_methods: List[str] = []
    path: str = None
    exclude_fields: List[str] = []
    join_related: Union[bool, List[str]] = []

    @validator('denied_methods')
    def denied_methods_validate(cls, v):
        correct_methods = {'get', 'post', 'delete', 'put', 'patch'}
        if len(v) > 0 and set(v) - correct_methods:
            raise ValueError('methods must be from list (\'get\', \'post\', \'delete\', \'put\', \'patch\')')

    @validator('pagination')
    def pagination_validate(cls, v):
        if v < 0:
            raise ValueError('value must be above or equal 0')

    @validator('join_related')
    def join_related_validate(cls, v):
        if v is False:
            raise ValueError('value must be True or List[str]')


class ModelValidator:
    def __init__(self, model):
        self.model = model
        self.errors = []
        self.base_config_properties = set(BaseConfigEndpoint.schema()['properties'])
        self.model_config_properties = {key for key in model.ConfigEndpoint.get_attrs()}
        self.config_properties = {key: getattr(model.ConfigEndpoint, key) for key in self.base_config_properties}
        self.validate()

    def validate(self):
        try:
            _ = BaseConfigEndpoint(**self.config_properties)
            self.validate_wrong_parameters()
            self.validate_exclude_fields()
        except Exception as e:
            for error in e.errors():
                error_msg = f'\'{" ".join(error["loc"])}\': {error["msg"]}'
                self.add_error(error_msg)

    def validate_wrong_parameters(self):
        wrong_parameters = self.model_config_properties - self.base_config_properties
        if len(wrong_parameters) > 0:
            msg = '\'{0}\': not support parameters'
            self.add_error(msg.format(', '.join(wrong_parameters)))

    def validate_exclude_fields(self):
        wrong_exclude_fields = set(self.model.ConfigEndpoint.exclude_fields) - {c.name for c in self.model.__table__.columns}
        if len(wrong_exclude_fields) > 0:
            msg = '\'exclude_fields\': not exists columns {0} in \'exclude_fields\' parameter'
            self.add_error(msg.format('[' + ', '.join(wrong_exclude_fields) + ']'))

    def add_error(self, error_msg):
        self.errors.append(f'Model \'{self.model.__name__}\' has incorrect ConfigEndpoint parameter {error_msg}')
