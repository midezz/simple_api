from sqlalchemy import create_engine, inspect, Table, Integer, String, MetaData, Column
from sqlalchemy.orm import sessionmaker, mapper
from models import TestModel

metadata = MetaData()

testclass = Table(
    'testmodel', metadata,
    Column('id', Integer, primary_key=True),
    Column('number', Integer),
    Column('name', String),
)


class TestClass:
    def __init__(self, number, name):
        self.number = number
        self.name = name


mapper(TestClass, testclass)

engine = create_engine('postgresql://pydantic_orm:123456@127.0.0.1/pydantic_test')
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

model = inspect(TestClass)

print('ok')
