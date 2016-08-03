import simplejson as json

from eve import STATUS_OK, LAST_UPDATED, ISSUES, STATUS, ETAG

from eve_neo4j.tests import TestBaseNeo4j


class TestPatch(TestBaseNeo4j):

    def test_patch_to_resource_endpoint(self):
        _, status = self.patch(self.known_resource_url, data={})
        self.assert405(status)

    def test_readonly_resource(self):
        _, status = self.patch(self.readonly_id_url, data={})
        self.assert405(status)

    def test_ifmatch_missing(self):
        _, status = self.patch(self.item_id_url, data={'key1': 'value1'})
        self.assert403(status)

    def test_ifmatch_bad_etag(self):
        _, status = self.patch(self.item_id_url,
                               data={'key1': 'value1'},
                               headers=[('If-Match', 'not-quite-right')])
        self.assert412(status)

    def test_patch_string(self):
        field = 'firstname'
        test_value = 'Douglas'
        changes = {field: test_value}
        r = self.perform_patch(changes)
        self.compare_patch_with_get(field, r)

    def test_patch_integer(self):
        field = "prog"
        test_value = 9999
        changes = {field: test_value}
        r = self.perform_patch(changes)
        db_value = self.compare_patch_with_get(field, r)
        self.assertEqual(db_value, test_value)

    def test_patch_datetime(self):
        field = "born"
        test_value = "Tue, 06 Nov 2012 10:33:31 GMT"
        changes = {field: test_value}
        r = self.perform_patch(changes)
        db_value = self.compare_patch_with_get(field, r)
        self.assertEqual(db_value, test_value)

    def test_patch_defaults(self):
        field = 'firstname'
        test_value = 'Douglas'
        changes = {field: test_value}
        r = self.perform_patch(changes)
        self.assertRaises(KeyError, self.compare_patch_with_get, 'title', r)

    def test_patch_multiple_fields(self):
        fields = ['firstname', 'prog']
        test_values = ['Douglas', 123]
        changes = {fields[0]: test_values[0], fields[1]: test_values[1]}
        r = self.perform_patch(changes)
        db_values = self.compare_patch_with_get(fields, r)
        for i in range(len(db_values)):
            self.assertEqual(db_values[i], test_values[i])

    def perform_patch(self, changes):
        r, status = self.patch(self.item_id_url,
                               data=changes,
                               headers=[('If-Match', self.item_etag)])
        self.assert200(status)
        self.assertPatchResponse(r, self.item_id)
        return r

    def perform_patch_with_post_override(self, field, value):
        headers = [('X-HTTP-Method-Override', 'PATCH'),
                   ('If-Match', self.item_etag),
                   ('Content-Type', 'application/json')]
        return self.test_client.post(self.item_id_url,
                                     data=json.dumps({field: value}),
                                     headers=headers)

    def compare_patch_with_get(self, fields, patch_response):
        raw_r = self.test_client.get(self.item_id_url)
        r, status = self.parse_response(raw_r)
        self.assert200(status)
        self.assertEqual(raw_r.headers.get('ETag'),
                         patch_response[ETAG])
        if isinstance(fields, str):
            return r[fields]
        else:
            return [r[field] for field in fields]

    def assertPatchResponse(self, response, item_id, resource=None):
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

    def patch(self, url, data, headers=[]):
        headers.append(('Content-Type', 'application/json'))
        r = self.test_client.patch(url,
                                   data=json.dumps(data),
                                   headers=headers)
        return self.parse_response(r)
