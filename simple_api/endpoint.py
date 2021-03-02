from sqlalchemy.ext.declarative import declared_attr


class Endpoint:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    class ConfigEndpoint:
        pegination = 100
        denied_methods = []
