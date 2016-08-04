# -*- coding: utf-8 -*-
from eve.io.mongo.validation import Validator
from eve.utils import config
from flask import current_app as app


class ValidatorNeo4j(Validator):
    """ An eve mongo Validator subclass adding Neo4j support to Cerberus
    standard validation.

    :param schema: the validation schema, to be composed according to Cerberus
                   documentation.
    :param resource: the resource name.
    """

    # Override validation for Mongo fields
    def _validate_type_objectid(self, field, value):
        self._error(field, "field objectid is not valid on Neo4j.")

    def _validate_type_dbref(self, field, value):
        self._error(field, "field dbref is not valid on Neo4j.")

    def _validate_type_point(self, field, value):
        self._error(field, "field point is not valid on Neo4j.")

    def _validate_type_geometrycollection(self, field, value):
        self._error(field, "field geometrycollection is not valid on Neo4j.")

    def _validate_type_multipolygon(self, field, value):
        self._error(field, "field multipolygon is not valid on Neo4j.")

    def _validate_type_multilinestring(self, field, value):
        self._error(field, "field multilinestring is not valid on Neo4j.")

    def _validate_type_multipoint(self, field, value):
        self._error(field, "field multipoint is not valid on Neo4j.")

    def _validate_type_polygon(self, field, value):
        self._error(field, "field polygon is not valid on Neo4j.")

    def _validate_type_linestring(self, field, value):
        self._error(field, "field linestring is not valid on Neo4j.")
