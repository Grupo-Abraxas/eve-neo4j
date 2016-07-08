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
    props = copy(properties)
    if config.DATE_CREATED in props:
        props[config.DATE_CREATED] = timestamp(props[config.DATE_CREATED])

    if config.LAST_UPDATED in props:
        props[config.LAST_UPDATED] = timestamp(props[config.LAST_UPDATED])

    return Node(label, **props)


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


def label(resource):
    if 'datasource' in config.DOMAIN[resource]:
        return config.DOMAIN[resource]['datasource'].get('source', resource)
    return resource
