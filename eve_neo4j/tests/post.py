# -*- coding: utf-8 -*-
import json
import random

from eve import STATUS_OK, LAST_UPDATED, ID_FIELD, ISSUES, \
    STATUS, ETAG

from eve_neo4j.tests import TestBaseNeo4j


class TestPostNeo4j(TestBaseNeo4j):

    def test_unknown_resource(self):
        _, status = self.post(self.unknown_resource_url, data={})
        self.assert404(status)

    def test_readonly_resource(self):
        _, status = self.post(self.readonly_resource_url, data={})
        self.assert405(status)

    def test_post_to_item_endpoint(self):
        _, status = self.post(self.item_id_url, data={})
        self.assert405(status)

    def test_validation_error(self):
        r, status = self.post(self.known_resource_url, data={'prog': 'a'})
        self.assertEqual(status, 422)
        self.assertValidationError(r, {'prog': 'must be of integer type'})

    def test_post_string(self):
        test_field = 'lastname'
        test_value = 'Adams'
        data = {test_field: test_value}
        self.assertPostItem(data, test_field, test_value)

    def test_post_integer(self):
        test_field = 'prog'
        test_value = 1
        data = {test_field: test_value}
        self.assertPostItem(data, test_field, test_value)

    def test_post_dict(self):
        test_field = 'address'
        test_value = {'address': 'an address', 'city': 'a city'}
        data = {test_field: test_value}
        self.assertPostItem(data, test_field, test_value)

    # TODO: Implement Neo4j json encoder to parse milliseconds from graph to
    # datetime -> string or return datetime on node_to_dict
    def test_post_datetime(self):
        test_field = "born"
        test_value = "Tue, 06 Nov 2012 10:33:31 GMT"
        data = {test_field: test_value}
        self.assertPostItem(data, test_field, test_value)

    def test_post_default_value(self):
        test_field = 'title'
        test_value = 'Mr.'
        data = {'firstname': 'Douglas'}
        self.assertPostItem(data, test_field, test_value)

    def test_post_default_value_empty_string(self):
        title = self.domain['people']['schema']['title']
        title['default'] = ''
        self.app.set_defaults()
        data = {'firstname': 'Douglas'}
        self.assertPostItem(data, 'title', '')

    def test_post_default_value_0(self):
        prog = self.domain['people']['schema']['prog']
        prog['default'] = 0
        self.app.set_defaults()
        data = {'firstname': 'Isaac'}
        self.assertPostItem(data, 'prog', 0)

    def test_multi_post(self):
        data = [
            {"firstname": "Douglas"},
            {"prog": 7},
            {"firstname": self.item_firstname, "lastname": 'Adams'}
        ]
        r, status = self.post(self.known_resource_url, data=data)
        self.assertEqual(status, 422)
        results = r['_items']

        self.assertEqual(results[0]['_status'], 'OK')
        self.assertEqual(results[1]['_status'], 'OK')

        # TODO: Implement Neo4j validator.
        self.assertValidationError(results[2], {'firstname': 'unique'})

        self.assertTrue(ID_FIELD not in results[0])
        self.assertTrue(ID_FIELD not in results[1])

        # items on which validation failed should not be inserted into the db
        _, status = self.get(self.known_resource_url,
                             'where=lastname=="Adams"')
        # self.assert404(status)

        # valid items part of a request containing invalid document should not
        # be inserted into the db
        _, status = self.get(self.known_resource_url, 'where=prog==7')
        # self.assert404(status)

    def test_post_x_www_form_urlencoded(self):
        test_field = 'firstname'
        test_value = 'Douglas'
        data = {test_field: test_value}
        r, status = self.parse_response(self.test_client.post(
            self.known_resource_url, data=data))
        self.assert201(status)
        self.assertTrue('OK' in r[STATUS])
        self.assertPostResponse(r)

    def test_post_allow_unknown(self):
        data = {"unknown": "unknown"}
        r, status = self.post(self.known_resource_url, data=data)
        self.assertEqual(status, 422)
        self.assertValidationError(r, {'unknown': 'unknown'})

    def test_post_with_content_type_charset(self):
        test_field = 'firstname'
        test_value = 'Douglas'
        data = {test_field: test_value}
        r, status = self.post(self.known_resource_url, data=data,
                              content_type='application/json; charset=utf-8')
        self.assert201(status)
        self.assertPostResponse(r)

    def test_post_with_extra_response_fields(self):
        self.domain['people']['extra_response_fields'] = ['firstname', 'nah']
        test_field = 'firstname'
        test_value = 'Douglas'
        data = {test_field: test_value}
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)
        self.assertTrue('firstname' in r)
        self.assertFalse('nah' in r)

    def test_post_with_get_override(self):
        # a GET request with POST override turns into a POST request.
        test_field = 'firstname'
        test_value = 'Douglas'
        data = json.dumps({test_field: test_value})
        headers = [('X-HTTP-Method-Override', 'POST'),
                   ('Content-Type', 'application/json')]
        r = self.test_client.get(self.known_resource_url, data=data,
                                 headers=headers)
        self.assert201(r.status_code)
        data = r.get_data()
        if isinstance(data, bytes):
            data = data.decode(encoding='UTF-8')
        self.assertPostResponse(json.loads(data))

    def test_custom_issues(self):
        self.app.config['ISSUES'] = 'errors'
        r, status = self.post(self.known_resource_url, data={"ref": "123"})
        self.assertEqual(status, 422)
        self.assertTrue('errors' in r and ISSUES not in r)

    def test_custom_status(self):
        self.app.config['STATUS'] = 'report'
        r, status = self.post(self.known_resource_url, data={"ref": "123"})
        self.assertEqual(status, 422)
        self.assertTrue('report' in r and STATUS not in r)

#    @skip('Custom etag updated not supported')
#    def test_custom_etag_update_date(self):
#        self.app.config['ETAG'] = '_myetag'
#        r, status = self.post(self.known_resource_url,
#                              data={"ref": "1234567890123456789054321"})
#        self.assert201(status)
#        self.assertTrue('_myetag' in r and ETAG not in r)

#    @skip('Custom date updated not supported')
#    def test_custom_date_updated(self):
#        self.app.config['LAST_UPDATED'] = '_update_date'
#        r, status = self.post(self.known_resource_url,
#                              data={"ref": "1234567890123456789054321"})
#        self.assert201(status)
#        self.assertTrue('_update_date' in r and LAST_UPDATED not in r)

    def test_post_ifmatch_disabled(self):
        # if IF_MATCH is disabled, then we get no etag in the payload.
        self.app.config['IF_MATCH'] = False
        test_field = 'ref'
        test_value = "1234567890123456789054321"
        data = {test_field: test_value}
        r, status = self.post(self.known_resource_url, data=data)
        self.assertTrue(ETAG not in r)

#    @skip('Custom ID_FIELD not supported')
#    def test_post_custom_idfield(self):
#        # test that we can post a document with a custom id_field
#        id_field = 'id'
#        test_value = '1234'
#        data = {id_field: test_value}
#
#        self.app.config['ID_FIELD'] = id_field
#
#        # custom id_fields also need to be included in the resource schema
#        self.domain['contacts']['schema'][id_field] = {
#            'type': 'string',
#            'required': True,
#            'unique': True
#        }
#        del(self.domain['contacts']['schema']['ref']['required'])
#
#        r, status = self.post(self.known_resource_url, data=data)
#        self.assert201(status)
#        self.assertTrue(id_field in r)
#        self.assertItemLink(r['_links'], r[id_field])

    def test_post_bandwidth_saver(self):
        data = {'number': random.randint(1000, 10000)}

        # bandwidth_saver is on by default
        self.assertTrue(self.app.config['BANDWIDTH_SAVER'])
        r, status = self.post('/invoices/', data=data)
        self.assert201(status)
        self.assertPostResponse(r)
        self.assertFalse('number' in r)

        # test return all fields (bandwidth_saver off)
        self.app.config['BANDWIDTH_SAVER'] = False
        r, status = self.post('/invoices/', data=data)
        self.assert201(status)
        self.assertPostResponse(r)
        self.assertTrue('number' in r)

    def test_post_create_relation(self):
        invoice_data = {'number': random.randint(1000, 10000)}

        # create new invoice
        invoice, status = self.post('/invoices/', data=invoice_data)
        self.assert201(status)
        self.assertPostResponse(invoice)
        self.assertTrue('_id' in invoice)

        # create (person)-[:has_invoice]->(invoice) relation wirth know item.
        relation_data = {
            'start_node': self.item_id,
            'end_node': invoice['_id'],
            'relation_property': 'test_value'
        }

        r, status = self.post('/userinvoices/', data=relation_data)
        self.assert201(status)
        self.assertPostResponse(r)
        self.assertTrue('_id' in r)

        # check type of created entity
        selector = self.app.data.driver
        graph = selector.graph
        start_node = selector.select('people', _id=self.item_id).first()
        end_node = selector.select('invoices', _id=invoice['_id']).first()

        relations = list(graph.match(start_node, 'has_invoice', end_node))
        self.assertEqual(len(relations), 1)

    def perform_post(self, data, valid_items=[0]):
        r, status = self.post(self.known_resource_url, data=data)
        self.assert201(status)
        self.assertPostResponse(r, valid_items)
        return r

    def assertPostItem(self, data, test_field, test_value):
        r = self.perform_post(data)
        item_id = r[ID_FIELD]
        item_etag = r[ETAG]
        db_value = self.compare_post_with_get(item_id, [test_field, ETAG])
        self.assertEqual(db_value[0], test_value)
        self.assertEqual(db_value[1], item_etag)

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
