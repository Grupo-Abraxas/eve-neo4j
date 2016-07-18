# -*- coding: utf-8 -*-
import eve
import os
import random
import string
import uuid

from datetime import datetime
from eve import ETAG
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

        response, _ = self.get(self.known_resource, '?max_results=2')
        person = self.response_item(response)
        self.item = person
        self.item_id = self.item[self.app.config['ID_FIELD']]
        self.item_firstname = self.item['firstname']
        self.item_etag = self.item[ETAG]
        self.item_id_url = ('/%s/%s' %
                            (self.domain[self.known_resource]['url'],
                             self.item_id))

        self.unknown_item_id = '05ced1a0-b16f-4ae8-8432-a80a84a947b2'
        self.unknown_resource = 'unknown'
        self.unknown_resource_url = '/%s' % self.unknown_resource

        self.readonly_resource = 'payments'
        self.readonly_resource_url = (
            '/%s' % self.domain[self.readonly_resource]['url'])

        response, _ = self.get('payments', '?max_results=1')
        self.readonly_id = self.response_item(response)['_id']
        self.readonly_id_url = ('%s/%s' % (self.readonly_resource_url,
                                           self.readonly_id))

        # self.epoch = date_to_str(datetime(1970, 1, 1))

    def response_item(self, response, i=0):
        if self.app.config['HATEOAS']:
            return response['_items'][i]
        else:
            return response[i]

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
            person['_id'] = str(uuid.uuid4())
            self.graph.create(person)

        # load random invoice
        try:
            dt = datetime.now().timestamp()
        except AttributeError:
            import time
            dt = time.mktime(datetime.now().timetuple())
        invoice = Node('invoice', number=random.randint(0, 100))
        invoice['people_id'] = people[0]['_id']
        invoice['_created'] = dt
        invoice['_updated'] = dt
        invoice['_id'] = str(uuid.uuid4())
        self.graph.create(invoice)

        # load random payments
        for _ in range(10):
            payment = Node(
                'payments', number=random.randint(0, 100),
                string=self.random_string(6))
            try:
                dt = datetime.now().timestamp()
            except AttributeError:
                import time
                dt = time.mktime(datetime.now().timetuple())
            payment['_created'] = dt
            payment['_updated'] = dt
            payment['_id'] = str(uuid.uuid4())
            self.graph.create(payment)

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
