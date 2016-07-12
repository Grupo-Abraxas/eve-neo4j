# -*- coding: utf-8 -*-
import uuid

from eve.io.base import DataLayer
from flask.ext import neo4j
from py2neo import NodeSelector

from eve_neo4j.structures import Neo4jResultCollection
from eve_neo4j.utils import label, id_field, dict_to_node, node_to_dict


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

    def find_one(self, resource, req, **lookup):
        """ Retrieves a single document/record. Consumed when a request hits an
        item endpoint (`/people/id/`).

        :param resource: resource being accessed. You should then use the
                         ``datasource`` helper function to retrieve both the
                         db collection/table and base query (filter), if any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). As we are going to only look for one document here,
                    the only req attribute that you want to process here is
                    ``req.projection``.

        :param **lookup: the lookup fields. This will most likely be a record
                         id or, if alternate lookup is supported by the API,
                         the corresponding query.
        """
        document = self.driver.select(resource, **lookup).first()
        return node_to_dict(document) if document else None

    def insert(self, resource, doc_or_docs):
        """ Inserts a document as a node with a label.

        :param resource: resource being accessed.
        :param doc_or_docs: json document or list of json documents to be added
                            to the database.
        """
        indexes = []
        lb = label(resource)
        for document in doc_or_docs:
            node = dict_to_node(lb, document)
            _id = str(uuid.uuid4())
            node[id_field(resource)] = _id
            self.driver.graph.create(node)
            indexes.append(_id)
        return indexes
