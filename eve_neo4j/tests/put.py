from bson import ObjectId
import simplejson as json

from eve.tests import TestBase
from eve.tests.test_settings import MONGO_DBNAME
from eve.tests.utils import DummyEvent

from eve import STATUS_OK, LAST_UPDATED, ISSUES, STATUS, ETAG
from eve.methods.put import put_internal

from eve_neo4j.tests import TestBaseNeo4j


class TestPut(TestBaseNeo4j):

    def test_put_string(self):
        field = "ref"
        test_value = "1234567890123456789012345"
        changes = {field: test_value}
        r = self.perform_put(changes)
        db_value = self.compare_put_with_get(field, r)
        self.assertEqual(db_value, test_value)

    def perform_put(self, changes):
        r, status = self.put(self.item_id_url,
                             data=changes,
                             headers=[('If-Match', self.item_etag)])
        self.assert200(status)
        self.assertPutResponse(r, self.item_id)
        return r

    def assertPutResponse(self, response, item_id, resource=None):
        id_field = self.domain[resource or self.known_resource]['id_field']
        self.assertTrue(STATUS in response)
        self.assertTrue(STATUS_OK in response[STATUS])
        self.assertFalse(ISSUES in response)
        self.assertTrue(id_field in response)
        self.assertEqual(response[id_field], item_id)
        self.assertTrue(LAST_UPDATED in response)
        self.assertTrue(ETAG in response)
        self.assertTrue('_links' in response)
        self.assertItemLink(response['_links'], item_id)

    def compare_put_with_get(self, fields, put_response):
        raw_r = self.test_client.get(self.item_id_url)
        r, status = self.parse_response(raw_r)
        self.assert200(status)
        self.assertEqual(raw_r.headers.get('ETag'),
                         put_response[ETAG])
        if isinstance(fields, str):
            return r[fields]
        else:
            return [r[field] for field in fields]
