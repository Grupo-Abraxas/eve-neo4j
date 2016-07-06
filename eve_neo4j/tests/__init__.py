# -*- coding: utf-8 -*-
import eve
import os
import random
import string

from datetime import datetime
from eve.tests import TestMinimal
from py2neo import Node

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
        self.domain = self.app.config['DOMAIN']
        self.known_resource_count = 101
        self.known_resource = 'people'
        self.known_resource_url = \
            '/%s' % self.domain[self.known_resource]['url']
        self.test_client = self.app.test_client()
        self.setupDB()

        self.empty_resource = 'empty'
        self.empty_resource_url = '/%s' % self.empty_resource

    def setupDB(self):
        self.graph = self.app.data.driver.graph
        self.bulk_insert()

    def tearDown(self):
        self.dropGraph()
        del self.app

    def dropGraph(self):
        self.graph.delete_all()

    def bulk_insert(self):
        people = self.random_people(self.known_resource_count)
        people = [Node(self.known_resource, **item) for item in people]
        for person in people:
            try:
                dt = datetime.now().timestamp()
            except AttributeError:
                import time
                dt = time.mktime(datetime.now().timetuple())
            person['_created'] = dt
            person['_updated'] = dt
            self.graph.create(person)

    def random_string(self, length=6):
        return ''.join(random.choice(string.ascii_lowercase)
                       for _ in range(length)).capitalize()

    def random_people(self, num):
        people = []
        for i in range(num):
            people.append({
                'firstname': self.random_string(6),
                'lastname': self.random_string(6)
            })
        return people
