# -*- coding: utf-8 -*-
import time

from copy import copy
from datetime import datetime
from eve.utils import config
from py2neo import Node


def node_to_dict(node):
    node = dict(node)
    if config.DATE_CREATED in node:
        node[config.DATE_CREATED] = datetime.fromtimestamp(
            node[config.DATE_CREATED])

    if config.LAST_UPDATED in node:
        node[config.LAST_UPDATED] = datetime.fromtimestamp(
            node[config.LAST_UPDATED])

    return node


def dict_to_node(label, properties={}):
    _properties = copy(properties)
    for k, v in _properties.items():
        if isinstance(v, datetime):
            _properties[k] = timestamp(v)

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
