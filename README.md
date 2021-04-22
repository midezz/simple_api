<img src="https://travis-ci.com/midezz/simple_api.svg?branch=master">

# SimpleRestApi

SimpleRestAPI is the library for launch REST API based on your SQLAlchemy models.

**Documentation:** <a href="https://simplerestapi.readthedocs.io/en/latest/">https://simplerestapi.readthedocs.io/en/latest/</a>

**Features**

* Minimum code. You don't need create any endpoints. All of you need is your SQLAlchemy models.
* You can customize your endpoints. For example, you can deny some methods or customize the endpoint's path.
* Under hood SimpleApi use Starlette.

**Installation**

```console
pip install simplerestapi
```

Also you need install uvicorn.

```console
pip install uvicorn
```


**Usage**

1. Create `models.py`
```Python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

from simplerestapi.endpoint import ConstructEndpoint, Endpoint

Base = declarative_base(metaclass=ConstructEndpoint)


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

```

2. Create `app.py`
```Python
import os

import uvicorn

import models
from simplerestapi.main import SimpleApi

app = SimpleApi(models, db='postgresql://db_user:db_pass@127.0.0.1/db_name')

```

3. Run application
```console
uvicorn app:app.app --reload
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [250901] using statreload
INFO:     Started server process [250903]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

4. Use REST API<br>
You can use methods GET, POST, PUT, PATCH, DELETE in endpoints:
* http://127.0.0.1:8000/car - GET for retrieve list of `models.Car` items, support filters, example `?name=SomeName`, POST for create new item in DB.
* http://127.0.0.1:8000/car/1 - GET for retrieve one item with id=1, also you can use PUT, PATCH for update item, DELETE for delete item from DB.

Similar endpoints are availible for all you models.
