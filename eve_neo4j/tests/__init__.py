# -*- coding: utf-8 -*-
import eve
import itertools
import os
import random
import string
import uuid

from datetime import datetime
from eve import ETAG
from eve.tests import TestMinimal
from py2neo import Node, Relationship

from eve_neo4j import Neo4j, ValidatorNeo4j
from eve_neo4j.utils import create_node


class TestBaseNeo4j(TestMinimal):

    def setUp(self, settings_file=None, url_converters=None):
        self.this_directory = os.path.dirname(os.path.realpath(__file__))
        self.settings_file = os.path.join(
            self.this_directory,
            'test_settings_neo4j.py')

        self.app = eve.Eve(
            settings=self.settings_file,
            url_converters=url_converters,
            data=Neo4j,
            validator=ValidatorNeo4j)
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
        self.dropIndexes()
        del self.app

    def dropGraph(self):
        self.graph.delete_all()

    def dropIndexes(self):
        schema = self.graph.schema
        for label in itertools.chain(
                self.graph.node_labels, self.graph.relationship_types):
            for property_ in schema.get_uniqueness_constraints(label):
                schema.drop_uniqueness_constraint(label, property_)

    def add_control_fields(self, entity):
        dt = datetime.now()
        entity['_created'] = dt
        entity['_updated'] = dt
        entity['_id'] = str(uuid.uuid4())

    def bulk_insert(self):
        tx = self.graph.begin()
        people = self.random_people(self.known_resource_count)
        [self.add_control_fields(person) for person in people]
        people = [
            create_node(self.known_resource, person) for person in people]
        [tx.create(person) for person in people]

        # load random invoice
        try:
            dt = datetime.now().timestamp()
        except AttributeError:
            import time
            dt = time.mktime(datetime.now().timetuple())
        invoice = Node('invoice', number=random.randint(0, 100))
        invoice['_created'] = dt
        invoice['_updated'] = dt
        invoice['_id'] = str(uuid.uuid4())
        relation = Relationship(people[0], 'has_invoice', invoice)
        tx.create(invoice | relation)

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
            tx.create(payment)
        tx.commit()

    def random_string(self, length=6):
        return ''.join(random.choice(string.ascii_lowercase)
                       for _ in range(length)).capitalize()

    def random_address(self):
        return {
            'address': self.random_string(),
            'city': self.random_string()
        }

    def random_people(self, num):
        people = []
        for i in range(num):
            person = {
                'firstname': self.random_string(6),
                'lastname': self.random_string(6),
                'address': self.random_address()
            }
            people.append(person)
        return people
