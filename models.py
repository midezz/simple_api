from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

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


if __name__ == '__main__':
    print('Start creating tables')
    engine = create_engine('postgresql://pydantic_orm:123456@127.0.0.1/pydantic_test')
    Base.metadata.create_all(engine)
    print('Tables created')
