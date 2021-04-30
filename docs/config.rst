.. _config:

Configuration endpoints
========================

Use ``class ConfigEndpoint`` to config your endpoints.

Example
--------------

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

        class ConfigEndpoint:
            denied_methods = ['put', 'get']
            path = '/new_custom_path'


In example above we use parameters:

* **denied_methods** - for deny methods `put` and `get`.
* **path** - for castomuze the path to access your endpoint. It means that your endpoint is available by http://127.0.0.1:8000/new_custom_path.


Default configuration
-------------------------

The default configuration is in code below.

.. code-block:: python

    class ConfigEndpoint:
        pagination = 100
        denied_methods = []
        path = None
        exclude_fields = []


Parameters
-------------

For customize your endpoint you can use a few parameters:

* **pagination** - This parameter config how many items from DB will show in one page. You can use the url parameter ``?page=`` for retrieving a certain page. Also to denying access to the list endpoint (http://127.0.0.1:8000/<table_name>) you need set ``pagination = 0``.
* **denied_methods** - This parameter config which methods are denied.
* **path** - This parameter customize url path to your endpoint. By default, ``path`` is equal ``/<table_name>`` for retrieving list items and creating the new item, ``/<table_name>/{id}`` for get, update, delete the item with ``id=1``.
* **exclude_fields** - This parameter config which fields of table doesn't return in the response. By default, all fields of the table will return in every response.
