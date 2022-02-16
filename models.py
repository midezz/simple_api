import os

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from simplerestapi.endpoint import ConstructEndpoint, Endpoint

Base = declarative_base(metaclass=ConstructEndpoint)


class CustomUser(Base, Endpoint):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    age = Column(Integer)
    car = relationship('Car', back_populates='customuser')

    class ConfigEndpoint:
        join_related = ['car']


class Car(Base, Endpoint):
    id = Column(Integer, primary_key=True)
    name_model = Column(String)
    production = Column(String)
    year = Column(Integer)
    customuser_id = Column(Integer, ForeignKey('customuser.id'))
    customuser = relationship('CustomUser', back_populates='car')

    class ConfigEndpoint:
        join_related = ['customuser']


if __name__ == '__main__':
    print('Start creating tables')
    engine = create_engine(os.environ['DB_URL_SYNC'])
    Base.metadata.create_all(engine)
    print('Tables created')
