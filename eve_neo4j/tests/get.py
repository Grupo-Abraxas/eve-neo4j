import json

from eve.utils import str_to_date
from py2neo import Node

from eve_neo4j.tests import TestBaseNeo4j


class TestGetNeo4j(TestBaseNeo4j):

    def test_get_empty_resource(self):
        response, status = self.get(self.empty_resource)
        self.assert404(status)

    def test_get_page(self):
        response, status = self.get(self.known_resource)
        self.assert200(status)

        links = response['_links']
        self.assertNextLink(links, 2)
        self.assertLastLink(links, 5)
        self.assertPagination(response, 1, 101, 25)

        page = 1
        response, status = self.get(self.known_resource,
                                    '?page=%d' % page)
        self.assert200(status)

        links = response['_links']
        self.assertNextLink(links, 2)
        self.assertLastLink(links, 5)
        self.assertPagination(response, 1, 101, 25)

        page = 2
        response, status = self.get(self.known_resource,
                                    '?page=%d' % page)
        self.assert200(status)

        links = response['_links']
        self.assertNextLink(links, 3)
        self.assertPrevLink(links, 1)
        self.assertLastLink(links, 5)
        self.assertPagination(response, 2, 101, 25)

        page = 5
        response, status = self.get(self.known_resource,
                                    '?page=%d' % page)
        self.assert200(status)

        links = response['_links']
        self.assertPrevLink(links, 4)
        self.assertLastLink(links, None)
        self.assertPagination(response, 5, 101, 25)

    def test_get_max_results(self):
        maxr = 10
        response, status = self.get(self.known_resource,
                                    '?max_results=%d' % maxr)
        self.assert200(status)

        resource = response['_items']
        self.assertEqual(len(resource), maxr)

        maxr = self.app.config['PAGINATION_LIMIT'] + 1
        response, status = self.get(self.known_resource,
                                    '?max_results=%d' % maxr)
        self.assert200(status)
        resource = response['_items']
        self.assertEqual(len(resource), self.app.config['PAGINATION_LIMIT'])

    def test_get_paging_disabled(self):
        self.app.config['DOMAIN'][self.known_resource]['pagination'] = False
        response, status = self.get(self.known_resource, '?page=2')
        self.assert200(status)
        resource = response['_items']
        self.assertFalse(len(resource) ==
                         self.app.config['PAGINATION_DEFAULT'])
        self.assertTrue(self.app.config['META'] not in response)
        links = response['_links']
        self.assertTrue('next' not in links)
        self.assertTrue('prev' not in links)

    def test_get_paging_disabled_no_args(self):
        self.app.config['DOMAIN'][self.known_resource]['pagination'] = False
        response, status = self.get(self.known_resource)
        self.assert200(status)
        resource = response['_items']
        self.assertEqual(len(resource), self.known_resource_count)
        self.assertTrue(self.app.config['META'] not in response)
        links = response['_links']
        self.assertTrue('next' not in links)
        self.assertTrue('prev' not in links)

    def test_get_where_disabled(self):
        self.app.config['DOMAIN'][self.known_resource]['allowed_filters'] = []
        where = 'firstname == %s' % self.item_firstname
        response, status = self.get(self.known_resource, '?where=%s' % where)
        self.assert200(status)
        resource = response['_items']
        self.assertEqual(len(resource), self.app.config['PAGINATION_DEFAULT'])

#    why it should be 304?
#    def test_get_if_modified_since(self):
#        self.assertIfModifiedSince(self.known_resource_url)

#    def test_cache_control(self):
#        self.assertCacheControl(self.known_resource_url)

    def test_expires(self):
        self.assertExpires(self.known_resource_url)

    def assert_get(self, response, status, resource=None):
        self.assert200(status)

        links = response['_links']
        self.assertEqual(len(links), 4)
        self.assertHomeLink(links)
        if not resource:
            resource = self.known_resource
        self.assertResourceLink(links, resource)
        self.assertNextLink(links, 2)

        resource = response['_items']
        self.assertEqual(len(resource), self.app.config['PAGINATION_DEFAULT'])

        for item in resource:
            self.assertItem(item)

        etag = item.get(self.app.config['ETAG'])
        self.assertTrue(etag is not None)

    def test_get_where_like(self):
        r = self.test_client.get("{0}{1}".format(
            self.known_resource_url,
            '?where={0}'.format(json.dumps({
                'firstname': 'like("john%")'
            }))
        ))
        self.assert200(r.status_code)

    def test_get_where_ilike(self):
        r = self.test_client.get("{0}{1}".format(
            self.known_resource_url,
            '?where={0}'.format(json.dumps({
                'firstname': 'ilike("john%")'
            }))
        ))
        self.assert200(r.status_code)

    def test_get_where_startswith(self):
        r = self.test_client.get("{0}{1}".format(
            self.known_resource_url,
            '?where={0}'.format(json.dumps({
                'firstname': 'startswith("john")'
            }))
        ))
        self.assert200(r.status_code)

    def test_get_custom_items(self):
        self.app.config['ITEMS'] = '_documents'
        response, _ = self.get(self.known_resource)
        self.assertTrue('_documents' in response and '_items' not in response)

    def test_get_custom_links(self):
        self.app.config['LINKS'] = '_navigation'
        response, _ = self.get(self.known_resource)
        self.assertTrue('_navigation' in response and '_links' not in response)

    def test_get_resource_title(self):
        # test that resource endpoints accepts custom titles.
        self.app.config['DOMAIN'][self.known_resource]['resource_title'] = \
            'new title'
        response, _ = self.get(self.known_resource)
        self.assertTrue('new title' in response['_links']['self']['title'])
        # test that the home page accepts custom titles.
        response, _ = self.get('/')
        found = False
        for link in response['_links']['child']:
            if link['title'] == 'new title':
                found = True
                break
        self.assertTrue(found)

    def test_get_idfield_doesnt_exist(self):
        # test that a non-existing ID_FIELD will be silently handled when
        # building HATEOAS document link (#351).
        self.app.config['ID_FIELD'] = 'id'
        response, status = self.get(self.known_resource)
        self.assert200(status)

    def test_get_invalid_idfield_cors(self):
        """ test that #381 is fixed. """
        request = '/%s/badid' % self.known_resource
        self.app.config['X_DOMAINS'] = '*'
        r = self.test_client.get(request, headers=[('Origin', 'test.com')])
        self.assert404(r.status_code)

    def test_documents_missing_standard_date_fields(self):
        """Documents created outside the API context could be lacking the
        LAST_UPDATED and/or DATE_CREATED fields.
        """
        graph = self.app.data.driver.graph
        firstname = 'Douglas'
        person = Node('people', firstname=firstname, lastname='Adams', prog=1)
        graph.create(person)
        where = '{"firstname": "%s"}' % firstname
        response, status = self.get(self.known_resource, '?where=%s' % where)
        self.assert200(status)
        resource = response['_items']
        self.assertEqual(len(resource), 1)
        # self.assertItem(resource[0], 'people')

    def test_cursor_extra_find(self):
        _find = self.app.data.find
        hits = {'total_hits': 0}

        def find(resource, req, sub_resource_lookup):
            def extra(response):
                response['_hits'] = hits
            cursor = _find(resource, req, sub_resource_lookup)
            cursor.extra = extra
            return cursor

        self.app.data.find = find
        r, status = self.get(self.known_resource)
        self.assert200(status)
        self.assertTrue('_hits' in r)
        self.assertEqual(r['_hits'], hits)


class TestGetItem(TestBaseNeo4j):

    def assertItemResponse(self, response, status, resource=None):
        self.assert200(status)
        self.assertTrue(self.app.config['ETAG'] in response)
        links = response['_links']
        self.assertEqual(len(links), 3)
        self.assertHomeLink(links)
        self.assertCollectionLink(links, resource or self.known_resource)
        self.assertItem(response, resource or self.known_resource)

    def test_disallowed_getitem(self):
        _, status = self.get(self.empty_resource, item=self.item_id)
        self.assert404(status)

    def test_getitem_by_id(self):
        response, status = self.get(self.known_resource,
                                    item=self.item_id)
        self.assertItemResponse(response, status)

        response, status = self.get(self.known_resource,
                                    item=self.unknown_item_id)
        self.assert404(status)

    def test_getitem_if_modified_since(self):
        self.assertIfModifiedSince(self.item_id_url)

    def test_getitem_if_none_match(self):
        r = self.test_client.get(self.item_id_url)
        etag = r.headers.get('ETag')
        self.assertTrue(etag is not None)
        r = self.test_client.get(self.item_id_url,
                                 headers=[('If-None-Match', etag)])
        self.assert304(r.status_code)
        self.assertTrue(not r.get_data())

    def test_cache_control(self):
        self.assertCacheControl(self.item_id_url)

    def test_expires(self):
        self.assertExpires(self.item_id_url)


class TestHead(TestBaseNeo4j):

    def test_head_home(self):
        self.assert_head('/')

    def test_head_resource(self):
        self.assert_head(self.known_resource_url)

    def test_head_item(self):
        self.assert_head(self.item_id_url)

    def assert_head(self, url):
        h = self.test_client.head(url)
        r = self.test_client.get(url)
        self.assertTrue(not h.data)

        if 'Expires' in r.headers:
            # there's a tiny chance that the two expire values will differ by
            # one second. See #316.
            head_expire = str_to_date(r.headers.pop('Expires'))
            get_expire = str_to_date(h.headers.pop('Expires'))
            d = head_expire - get_expire
            self.assertTrue(d.seconds in (0, 1))

        self.assertEqual(r.headers, h.headers)
