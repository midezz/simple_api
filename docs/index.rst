Welcome to SimpleApi's documentation!
=====================================

SimpleAPI is the library for launch REST API based on your SQLAlchemy models.

.. toctree::

   test
   test2


   


 
Features
----------

* Minimum code. You don't need create any endpoints. All of you need is your SQLAlchemy models.
* You can customize your endpoints. For example, you can deny some methods or customize the endpoint's path.
* Under hood SimpleApi use Starlette.

Installation
------------

.. code-block:: console

   pip install simple_api


Also you need install uvicorn.

.. code-block:: console

   pip install uvicorn


Usage
---------

1. Create ``models.py``

.. code-block:: python

   from sqlalchemy import Column, Integer, String, create_engine
   from sqlalchemy.ext.declarative import declarative_base

   from simple_api.endpoint import ConstructEndpoint, Endpoint

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

2. Create ``app.py``
   
.. code-block:: python

   import os

   import uvicorn

   import models
   from simple_api.main import SimpleApi

   app = SimpleApi(models, db='postgresql://db_user:db_pass@127.0.0.1/db_name')

3. Run application
   
.. code-block:: console

   uvicorn app:app.app --reload
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process [250901] using statreload
   INFO:     Started server process [250903]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.


4. Use REST API. You can use methods GET, POST, PUT, PATCH, DELETE in endpoints:

   * http://127.0.0.1:8000/car - GET for retrieve list of `models.Car` items, support filters in url, example `?name=SomeName`, POST for create new item in DB.
   * http://127.0.0.1:8000/car/1 - GET for retrieve one item with `id=1`, also you can use PUT, PATCH for update item, DELETE for delete item from DB.<br>
   * Similar endpoints are availible for all you models.