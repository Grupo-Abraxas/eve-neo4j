# -*- coding: utf-8 -*-
from eve_neo4j.utils import node_to_dict, count_selection


class Neo4jResultCollection(object):
    """
    Collection of results. The object holds onto a py2neo-NodeSelection
    object and serves a generator off it.

    :param selection: NodeSelection object for the requested resource.
    """

    def __init__(self, selection, **kwargs):
        self._selection = selection

    def __iter__(self):
        for node in self._selection:
            yield node_to_dict(node)

    def count(self, with_limit_and_skip=False, **kwargs):
        return count_selection(self._selection, with_limit_and_skip)
