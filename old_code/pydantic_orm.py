from pydantic import BaseModel
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, inspect, create_engine
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = MetaData()


def get_type(field):
    if field.type_ is int:
        return Integer
    if field.type_ is str:
        return String
    if field.type_ is float:
        return Float


class PydanticORM(BaseModel):
    def __new__(cls, *args, **kwargs):
        if 'id' in cls.__fields__:
            raise Exception('Field name "id" is denied to use')
        table = cls.constructtable()
        mapper(cls, table)
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        engine = create_engine('postgresql://pydantic_orm:123456@127.0.0.1/pydantic_test')
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        for key, value in self.__fields__.items():
            print(value.type_, key)
        print('it\'s my class')

    @classmethod
    def constructtable(cls):
        tablename = cls.__name__.lower()
        columns = cls.get_columns()
        table = Table(
            tablename,
            metadata,
            Column('id', Integer, primary_key=True),
            *columns,
        )
        return table

    @classmethod
    def get_columns(cls):
        columns = []
        for key, value in cls.__fields__.items():
            columns.append(Column(key, get_type(value)))
        return columns
