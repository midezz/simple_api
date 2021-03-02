from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from simple_api import Endpoint


Base = declarative_base()


class CustomUser(Base, Endpoint):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    age = Column(Integer)


class Car(Base, Endpoint):
    id = Column(Integer, primary_key=True)
    name_model = Column(String)
    production = Column(String)
    year = Column(Integer)
