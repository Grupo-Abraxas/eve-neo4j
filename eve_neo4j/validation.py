# -*- coding: utf-8 -*-
from eve.io.mongo.validation import Validator
from eve.utils import config
from flask import current_app as app

from eve_neo4j.utils import count_selection


class ValidatorNeo4j(Validator):
    """ An eve mongo Validator subclass adding Neo4j support to Cerberus
    standard validation.

    :param schema: the validation schema, to be composed according to Cerberus
                   documentation.
    :param resource: the resource name.
    """

    def _is_value_unique(self, unique, field, value, query):
        """ Validates that a field value is unique.
        """
        if unique:
            query[field] = value

            resource_config = config.DOMAIN[self.resource]

            label, _, _, _ = app.data.datasource(self.resource)
            selected = app.data.driver.select(label, **query)

            # exclude current document
            if self._id:
                id_field = resource_config['id_field']
                selected = selected.where(
                    '_.%s <> "%s"' % (id_field, self._id))

            if count_selection(selected) > 0:
                self._error(field, "value '%s' is not unique" % value)

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
