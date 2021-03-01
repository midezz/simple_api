from pydantic_orm import PydanticORM
from pydantic import BaseModel
from sqlalchemy import MetaData, Table, Column, String, create_engine, Integer
from sqlalchemy.orm import mapper, sessionmaker
from dataclasses import dataclass
from my_orm import TestORM

metadata = MetaData()

table = Table(
    'custom_user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('surname', String),
    Column('age', Integer),
)
engine = create_engine('postgresql://pydantic_orm:123456@127.0.0.1/pydantic_test')
metadata.create_all(engine)


class CustomUser:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname



class NewCustomUser(TestORM):
    name: str
    surname: str
    age: int


# mapper(NewCustomUser, table)


user = NewCustomUser(name='Test', surname='New test', age=15)


Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
# session.add(user)
# session.commit()



print('test')


print('ok')
