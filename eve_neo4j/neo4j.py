# -*- coding: utf-8 -*-
import json
import uuid

from datetime import datetime
from eve.io.base import DataLayer
from eve.utils import debug_error_message, str_to_date
from flask import abort
from flask.ext import neo4j
from py2neo import NodeSelector

from eve_neo4j.structures import Neo4jResultCollection
from eve_neo4j.utils import id_field, create_node, node_to_dict, \
    timestamp


class Neo4j(DataLayer):
    """Neo4j data layer access for Eve REST API.
    """

    serializers = {
        'datetime': str_to_date,
        'integer': lambda value: int(value) if value is not None else None,
        'float': lambda value: float(value) if value is not None else None,
    }

    def init_app(self, app):
        """Initialize Neo4j.
        """
        graph = neo4j.Neo4j(app).gdb
        self.driver = NodeSelector(graph)

        self.register_schema(app)

    def register_schema(self, app):
        """Register schema for Neo4j indexes.

        :param app: Flask application instance.
        """
        for k, v in app.config['DOMAIN'].items():
            if 'datasource' in v and 'source' in v['datasource']:
                label = v['datasource']['source']
            else:
                label = k

            if 'id_field' in v:
                id_field = v['id_field']
            else:
                id_field = app.config['ID_FIELD']

            try:
                self.driver.graph.schema.create_uniqueness_constraint(
                    label, id_field)
            except Exception:
                pass

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
        label, filter_, fields, sort = self._datasource_ex(resource, [])
        selected = self.driver.select(label)

        if req.where:
            properties = json.loads(req.where)
            selected = selected.where(**properties)

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
        label, _, _, _ = self._datasource_ex(resource, [])
        for document in doc_or_docs:
            node = create_node(label, document)
            _id = str(uuid.uuid4())
            node[id_field(resource)] = _id
            self.driver.graph.create(node)
            indexes.append(_id)
        return indexes

    def update(self, resource, id_, updates, original):
        """ Updates a graph node.
        :param resource: resource being accessed.
        :param id_: the unique id of the node.
        :param updates: json updates to be performed on the node.
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        label, _, _, _ = self._datasource_ex(resource, [])
        id_field = self.app.config['ID_FIELD']
        filter_ = {id_field: id_}
        node = self.driver.select(label, **filter_).first()
        if node is None:
            abort(500, description=debug_error_message('Object not existent'))
        # node = node_to_dict(node)
        for k, v in updates.items():
            if isinstance(v, datetime):
                v = timestamp(v)
            node[k] = v
        self.driver.graph.push(node)

    def replace(self, resource, id_, document, original):
        """ Replaces a graph node.

        :param resource: resource being accessed.
        :param id_: the unique id of the node.
        :param document: the new json document
        :param original: definition of the json document that should be
                         updated.
        :raise OriginalChangedError: raised if the database layer notices a
                                     change from the supplied `original`
                                     parameter.
        """
        label, _, _, _ = self._datasource_ex(resource, [])
        id_field = self.app.config['ID_FIELD']
        filter_ = {id_field: id_}
        old_node = self.driver.select(label, **filter_).first()

        # Delete the old node
        if old_node is None:
            abort(500, description=debug_error_message('Object not existent'))
        self.driver.graph.delete(old_node)

        # create and insert the new one
        node = create_node(label, document)
        node[id_field] = id_
        self.driver.graph.create(node)

    def remove(self, resource, lookup={}):
        """ Removes a node or an entire set of nodes from a graph label.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param lookup: a dict with the query that documents must match in order
                       to qualify for deletion. For single document deletes,
                       this is usually the unique id of the document to be
                       removed.
        """
        datasource, filter_, _, _ = self._datasource_ex(resource, lookup)
        nodes = self.driver.select(datasource, **filter_)
        tx = self.driver.graph.begin()
        for node in nodes:
            tx.delete(node)
        tx.commit()
