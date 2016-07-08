# -*- coding: utf-8 -*-
import json

from eve import STATUS_OK, LAST_UPDATED, ID_FIELD, DATE_CREATED, ISSUES, \
    STATUS, ETAG
from pprint import pprint

from eve_neo4j.tests import TestBaseNeo4j


class TestPostNeo4j(TestBaseNeo4j):

    def test_post_string(self):
        test_field = 'lastname'
        test_value = 'Adams'
        data = {test_field: test_value}
        self.assertPostItem(data, test_field, test_value)

    def perform_post(self, data, valid_items=[0]):
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)
        self.assertPostResponse(r, valid_items)
        return r

    def assertPostItem(self, data, test_field, test_value):
        r = self.perform_post(data)
        item_id = r[ID_FIELD]
        item_etag = r[ETAG]
        # db_value = self.compare_post_with_get(item_id, [test_field, ETAG])
        # self.assertEqual(db_value[0], test_value)
        # self.assertEqual(db_value[1], item_etag)

    def assertPostResponse(self, response, valid_items=[0], resource=None):
        if '_items' in response:
            results = response['_items']
        else:
            results = [response]

        id_field = self.domain[resource or self.known_resource]['id_field']

        for i in valid_items:
            item = results[i]
            self.assertTrue(STATUS in item)
            self.assertTrue(STATUS_OK in item[STATUS])
            self.assertFalse(ISSUES in item)
            self.assertTrue(id_field in item)
            self.assertTrue(LAST_UPDATED in item)
            self.assertTrue('_links' in item)
            self.assertItemLink(item['_links'], item[id_field])
            self.assertTrue(ETAG in item)

    def compare_post_with_get(self, item_id, fields):
        raw_r = self.test_client.get(
            '%s/%s' % (self.known_resource_url, item_id))
        item, status = self.parse_response(raw_r)
        self.assert200(status)
        self.assertTrue(ID_FIELD in item)
        self.assertTrue(item[ID_FIELD] == item_id)
        if isinstance(fields, list):
            return [item[field] for field in fields]
        else:
            return item[fields]

    def post(self, url, data, headers=[], content_type='application/json'):
        headers.append(('Content-Type', content_type))
        r = self.test_client.post(
            url,
            data=json.dumps(data),
            headers=headers)
        return self.parse_response(r)
