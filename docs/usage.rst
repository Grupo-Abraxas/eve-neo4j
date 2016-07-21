=====
Usage
=====

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
