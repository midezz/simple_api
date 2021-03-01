from dataclasses import dataclass
from abc import ABCMeta
from sqlalchemy import Integer, String, Float, Column, Table, MetaData
from sqlalchemy.orm import mapper

metadata = MetaData()



def get_type(field):
    if field is int:
        return Integer
    if field is str:
        return String
    if field is float:
        return Float


def get_columns(fields):
    columns = []
    for key, value in fields.items():
        columns.append(Column(key, get_type(value)))
    return columns


class MetaORM(ABCMeta):
    def __new__(cls, name, bases, namespace, **kwargs):
        print('meta class')
        if name != 'TestORM':
            fields = get_columns(namespace['__annotations__'])
            namespace['__table__'] = cls.constructtable(name, fields)
        return super().__new__(cls, name, bases, namespace, **kwargs)

    @classmethod
    def constructtable(cls, name, fields):
        table = Table(
            name.lower(),
            metadata,
            Column('id', Integer, primary_key=True),
            *fields,
        )
        return table

@dataclass
class TestORM(metaclass=MetaORM):
    test = {}

    def __new__(cls, *args, **kwargs):
        mapper(cls, cls.__table__)
        return cls

