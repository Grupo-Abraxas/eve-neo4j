from eve import STATUS_OK, LAST_UPDATED, ISSUES, STATUS, ETAG

from eve_neo4j.tests import TestBaseNeo4j


class TestPut(TestBaseNeo4j):
    # TODO consider making a base codebase out of 'patch' and 'put' tests
    def test_put_to_resource_endpoint(self):
        _, status = self.put(self.known_resource_url, data={})
        self.assert405(status)

    def test_readonly_resource(self):
        _, status = self.put(self.readonly_id_url, data={})
        self.assert405(status)

    def test_ifmatch_missing(self):
        _, status = self.put(self.item_id_url, data={'key1': 'value1'})
        self.assert403(status)

    def test_ifmatch_disabled(self):
        self.app.config['IF_MATCH'] = False
        r, status = self.put(self.item_id_url,
                             data={'ref': '1234567890123456789012345'})
        self.assert200(status)
        self.assertTrue(ETAG not in r)

    def test_ifmatch_bad_etag(self):
        _, status = self.put(self.item_id_url,
                             data={'key1': 'value1'},
                             headers=[('If-Match', 'not-quite-right')])
        self.assert412(status)

    def test_allow_unknown(self):
        changes = {"unknown": "unknown"}
        r, status = self.put(self.item_id_url, data=changes,
                             headers=[('If-Match', self.item_etag)])
        self.assertValidationErrorStatus(status)
        self.assertValidationError(r, {'unknown': 'unknown field'})
        self.app.config['DOMAIN'][self.known_resource]['allow_unknown'] = True
        changes = {"unknown": "unknown", "ref": "1234567890123456789012345"}
        r, status = self.put(self.item_id_url, data=changes,
                             headers=[('If-Match', self.item_etag)])
        self.assert200(status)
        self.assertPutResponse(r, self.item_id)

    def test_put_x_www_form_urlencoded(self):
        field = "ref"
        test_value = "1234567890123456789012345"
        changes = {field: test_value}
        headers = [('If-Match', self.item_etag)]
        r, status = self.parse_response(self.test_client.put(
            self.item_id_url, data=changes, headers=headers))
        self.assert200(status)
        self.assertTrue('OK' in r[STATUS])

    def test_put_string(self):
        field = "ref"
        test_value = "1234567890123456789012345"
        changes = {field: test_value}
        r = self.perform_put(changes)
        db_value = self.compare_put_with_get(field, r)
        self.assertEqual(db_value, test_value)

    def test_put_default_value(self):
        test_field = 'title'
        test_value = "Mr."
        data = {'ref': '9234567890123456789054321'}
        r = self.perform_put(data)
        db_value = self.compare_put_with_get(test_field, r)
        self.assertEqual(test_value, db_value)

    def test_put_bandwidth_saver(self):
        changes = {'ref': '1234567890123456789012345'}

        # bandwidth_saver is on by default
        self.assertTrue(self.app.config['BANDWIDTH_SAVER'])
        r = self.perform_put(changes)
        self.assertFalse('ref' in r)
        db_value = self.compare_put_with_get(self.app.config['ETAG'], r)
        self.assertEqual(db_value, r[self.app.config['ETAG']])
        self.item_etag = r[self.app.config['ETAG']]

        # test return all fields (bandwidth_saver off)
        self.app.config['BANDWIDTH_SAVER'] = False
        r = self.perform_put(changes)
        self.assertTrue('ref' in r)
        db_value = self.compare_put_with_get(self.app.config['ETAG'], r)
        self.assertEqual(db_value, r[self.app.config['ETAG']])

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
