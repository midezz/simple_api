import models
import sys, inspect
from sqlalchemy.orm import sessionmaker


data = []

for name, member in inspect.getmembers(models):
    if inspect.isclass(member):
        if member.__module__ == 'models':
            data.append(member)


Session = sessionmaker()
Session.configure(bind=models.engine)
session = Session()
table = data[0]



print('test')