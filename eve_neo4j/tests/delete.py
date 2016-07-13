from eve.tests.utils import DummyEvent
from eve.tests.test_settings import MONGO_DBNAME
from eve import ETAG
from bson import ObjectId
from eve.utils import ParsedRequest
import simplejson as json
import copy

from eve.methods.delete import deleteitem_internal
from eve_neo4j.tests import TestBaseNeo4j


class TestDelete(TestBaseNeo4j):
    def setUp(self):
        super(TestDelete, self).setUp()
        # Etag used to delete an item (a contact)
        self.etag_headers = [('If-Match', self.item_etag)]

    def test_delete_from_resource_endpoint(self):
        r, status = self.delete(self.known_resource_url)
        self.assert204(status)
        r, status = self.parse_response(self.test_client.get(
            self.known_resource_url))
        self.assert200(status)
        self.assertEqual(len(r['_items']), 0)
