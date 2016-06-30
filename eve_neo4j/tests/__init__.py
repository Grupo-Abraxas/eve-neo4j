# -*- coding: utf-8 -*-
import eve
import os

from eve.tests import TestMinimal

from eve_neo4j import Neo4j


class TestBaseNeo4j(TestMinimal):

    def setUp(self, settings_file=None, url_converters=None):
        self.this_directory = os.path.dirname(os.path.realpath(__file__))
        self.settings_file = os.path.join(
            self.this_directory,
            'test_settings_neo4j.py')

        self.app = eve.Eve(
            settings=self.settings_file,
            url_converters=url_converters,
            data=Neo4j)
        self.test_client = self.app.test_client()
        self.domain = self.app.config['DOMAIN']

        self.known_resource = 'people'
        self.known_resource_url = \
            '/%s' % self.domain[self.known_resource]['url']
