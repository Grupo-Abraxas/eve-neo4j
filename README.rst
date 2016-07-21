===============================
Eve Neo4j extension.
===============================


.. image:: https://img.shields.io/pypi/v/eve_neo4j.svg
        :target: https://pypi.python.org/pypi/eve_neo4j

.. image:: https://travis-ci.org/Abraxas-Biosystems/eve-neo4j.svg?branch=master
    :target: https://travis-ci.org/Abraxas-Biosystems/eve-neo4j

.. image:: https://readthedocs.org/projects/eve-neo4j/badge/?version=latest
    :target: http://eve-neo4j.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://pyup.io/repos/github/abraxas-biosystems/eve-neo4j/shield.svg
     :target: https://pyup.io/repos/github/abraxas-biosystems/eve-neo4j/
     :alt: Updates

.. image:: https://pyup.io/repos/github/abraxas-biosystems/eve-neo4j/python-3-shield.svg
     :target: https://pyup.io/repos/github/abraxas-biosystems/eve-neo4j/
     :alt: Python 3

Eve-Neo4j is a Neo4j data layer for eve REST framework.

Features
--------

* Neo4j's nodes CRUD.

License
-------

* `MIT license <LICENSE>`_

Install
-------

.. code-block:: bash

    $ pip install eve-neo4j

Usage
-----

Set neo4j as your eve data layer.

.. code-block:: python

    import eve
    from eve_neo4j import Neo4j

    app = eve.Eve(data=Neo4j)
    app.run()

Config
------

.. code-block:: python

    GRAPH_DATABASE = 'http://localhost:7474/db/data/'
    GRAPH_USER = 'neo4j'
    GRAPH_PASSWORD = 'neo4j'

    # TODO: Override this as a defautl when ussing Neo4j as datalayer
    ITEM_URL = 'regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")'
