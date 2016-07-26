# -*- coding: utf-8 -*-
from cerberus import Validator
from collections import Mapping
from eve.utils import config


class ValidatorNeo4j(Validator):
    """ A cerberus Validator subclass adding the 'relation' type to Cerberus
    standard validation.

    :param schema: the validation schema, to be composed according to Cerberus
                   documentation.
    :param resource: the resource name.
    """

    def __init__(self, schema=None, resource=None, allow_unknown=False,
                 transparent_schema_rules=False):
        self.resource = resource
        self._id = None
        self._original_document = None

        if resource:
            transparent_schema_rules = \
                config.DOMAIN[resource]['transparent_schema_rules']
            allow_unknown = config.DOMAIN[resource]['allow_unknown']
        super(ValidatorNeo4j, self).__init__(
            schema,
            transparent_schema_rules=transparent_schema_rules,
            allow_unknown=allow_unknown)

    def validate_update(self, document, _id, original_document=None):
        """ Validate method to be invoked when performing an update, not an
        insert.

        :param document: the document to be validated.
        :param _id: the unique id of the document.
        """
        self._id = _id
        self._original_document = original_document
        return super(ValidatorNeo4j, self).validate_update(document)

    def validate_replace(self, document, _id, original_document=None):
        """ Validation method to be invoked when performing a document
        replacement. This differs from :func:`validation_update` since in this
        case we want to perform a full :func:`validate` (the new document is to
        be considered a new insertion and required fields needs validation).
        However, like with validate_update, we also want the current _id
        not to be checked when validationg 'unique' values.
        """
        self._id = _id
        self._original_document = original_document
        return super(ValidatorNeo4j, self).validate(document)

    def _validate_default(self, unique, field, value):
        """ Fake validate function to let cerberus accept "default"
            as keyword in the schema
        """
        pass

    def _validate_versioned(self, unique, field, value):
        """ Fake validate function to let cerberus accept "versioned"
            as keyword in the schema
        """
        pass

    def _validate_type_objectid(self, field, value):
        """ Enables validation for `objectid` data type.

        :param field: field name.
        :param value: field value.

        """
        pass

    def _validate_data_relation(self, data_relation, field, value):
        """ Enables validation for `data_relation` field attribute. Makes sure
        'value' of 'field' adheres to the referential integrity rule specified
        by 'data_relation'.

        :param data_relation: a dict following keys:
            'resource': foreign resource name
            'field': foreign field name
            'version': True if this relation points to a specific version
            'type': the type for the reference field if 'version': True
        :param field: field name.
        :param value: field value.
        """
        # TODO Validate data_relation
        pass

    def _validate_type_relation(self, field, value):
        """Enables validation for 'relation' data type.

        :param field: field name.
        :param value: field value.
        """
        if isinstance(value, Mapping):
            return True

    def _validate_datasource(self, datasource, field, value):
        """Enables validation for `datasource` schema attribute.

        :param datasource:
        :param field:
        :param value:
        """
        pass
