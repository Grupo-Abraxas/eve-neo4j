# -*- coding: utf-8 -*-
from eve_neo4j.tests import TestBaseNeo4j


class TestDelete(TestBaseNeo4j):
    def setUp(self):
        super(TestDelete, self).setUp()
        # Etag used to delete an item (a contact)
        self.etag_headers = [('If-Match', self.item_etag)]

    def test_unknown_resource(self):
        url = '%s%s/' % (self.unknown_resource_url, self.item_id)
        _, status = self.delete(url)
        self.assert404(status)

    def test_delete_from_resource_endpoint(self):
        r, status = self.delete(self.known_resource_url)
        self.assert204(status)
        r, status = self.parse_response(self.test_client.get(
            self.known_resource_url))
        self.assert200(status)
        self.assertEqual(len(r['_items']), 0)

    def test_delete_empty_resource(self):
        url = '%s%s/' % (self.empty_resource_url, self.item_id)
        _, status = self.delete(url)
        self.assert404(status)

    def test_delete_readonly_resource(self):
        _, status = self.delete(self.readonly_id_url)
        self.assert405(status)

    def test_delete_readonly_resource_with_override(self):
        headers = [('X-HTTP-Method-Override', 'DELETE')]
        r = self.test_client.get(self.readonly_resource_url, headers=headers)
        self.assert405(r.status_code)

    def test_delete_unknown_item(self):
        url = '%s%s/' % (self.known_resource_url, self.unknown_item_id)
        _, status = self.delete(url)
        self.assert404(status)

    def test_delete_ifmatch_missing(self):
        _, status = self.delete(self.item_id_url)
        self.assert403(status)

    def test_delete_ifmatch_disabled(self):
        self.app.config['IF_MATCH'] = False
        _, status = self.delete(self.item_id_url)
        self.assert204(status)

    def test_delete_ifmatch_bad_etag(self):
        _, status = self.delete(self.item_id_url,
                                headers=[('If-Match', 'not-quite-right')])
        self.assert412(status)

    def test_delete(self):
        r, status = self.delete(self.item_id_url, headers=self.etag_headers)
        self.assert204(status)

        r = self.test_client.get(self.item_id_url)
        self.assert404(r.status_code)

    def test_delete_non_existant(self):
        url = self.item_id_url[:-5] + "00000"
        r, status = self.delete(url, headers=self.etag_headers)
        self.assert404(status)

    def test_delete_with_post_override(self):
        # POST request with DELETE override turns into a DELETE
        headers = [('X-HTTP-Method-Override', 'DELETE'),
                   ('If-Match', self.item_etag)]
        r = self.test_client.post(self.item_id_url, data={}, headers=headers)
        self.assert204(r.status_code)

    def delete(self, url, headers=None):
        r = self.test_client.delete(url, headers=headers)
        return self.parse_response(r)
