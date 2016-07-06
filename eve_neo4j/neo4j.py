# -*- coding: utf-8 -*-
from eve.io.base import DataLayer
from flask.ext import neo4j
from py2neo import NodeSelector

from eve_neo4j.structures import Neo4jResultCollection


class Neo4j(DataLayer):
    """Neo4j data layer access for Eve REST API.
    """

    def init_app(self, app):
        """Initialize Neo4j.
        """
        graph = neo4j.Neo4j(app).gdb
        self.driver = NodeSelector(graph)

    def find(self, resource, req, sub_resource_lookup):
        """ Retrieves a set of documents matching a given request.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the db collection/table and base query (filter), if
                         any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). Be warned that `where` and `sort` expresions will
                    need proper parsing, according to the syntax that you want
                    to support with your driver. For example ``eve.io.Mongo``
                    supports both Python and Mongo-like query syntaxes.
        :param sub_resource_lookup: sub-resoue lookup from the endpoint url.
        """
        selected = self.driver.select(resource)

        if req.max_results:
            selected = selected.limit(req.max_results)

        if req.page > 1:
            selected = selected.skip((req.page - 1) * req.max_results)

        return Neo4jResultCollection(selected)
