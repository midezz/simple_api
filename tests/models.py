from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from simplerestapi.endpoint import ConstructEndpoint, Endpoint

Base = declarative_base(metaclass=ConstructEndpoint)


class CustomUser(Base, Endpoint):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    age = Column(Integer)
    car = relationship('Car')


class Car(Base, Endpoint):
    id = Column(Integer, primary_key=True)
    name_model = Column(String)
    production = Column(String)
    year = Column(Integer, nullable=False)
    customuser_id = Column(Integer, ForeignKey('customuser.id'))
    customuser = relationship('CustomUser')
