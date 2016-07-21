# -*- coding: utf-8 -*-
import time

from copy import copy
from datetime import datetime
from eve.utils import config
from py2neo import Node


def resource_for_label(label):
    """
    Return resource for the given label.

    :param label:
    """
    for k, v in  config.DOMAIN.items():
        if (v['datasource'] and v['datasource'].get('source') == label) or \
                k == label:
            return k

def node_to_dict(node):
    """
    Convert a Node to a dict.
    Parse datetime fields from timestamp to datetime objects.

    :param node: Node to be parsed.
    """
    resource = resource_for_label(list(node.labels())[0])
    schema = config.DOMAIN[resource]['schema']
    node = dict(node)
    for k, v in node.items():
        if k == config.DATE_CREATED or k == config.LAST_UPDATED or \
                schema.get(k, {}).get('type') == 'datetime':
            node[k] = datetime.fromtimestamp(v)

    return node


def prepare_properties(properties):
    """
    Prepare properties for a node.

    :param properties: dict with properties for a node.
    """
    _properties = copy(properties)
    for k, v in _properties.items():
        if isinstance(v, datetime):
            _properties[k] = timestamp(v)

    return _properties


def create_node(label, properties={}):
    """
    Create a Node with the given properties using the given label.

    :param label:
    :param properties:
    """
    _properties = prepare_properties(properties)

    return Node(label, **_properties)


def timestamp(value):
    try:
        return value.timestamp()
    except AttributeError:
        return time.mktime(value.timetuple())


def count_selection(selection, with_limit_and_skip=False):
    if not with_limit_and_skip:
        selection = copy(selection)
        selection._skip = None
        selection._limit = None
    query, params = selection._query_and_parameters
    query = query.replace("RETURN _", "RETURN COUNT(_)")
    return selection.graph.evaluate(query, params)


def id_field(resource):
    return config.DOMAIN[resource].get('id_field', config.ID_FIELD)
