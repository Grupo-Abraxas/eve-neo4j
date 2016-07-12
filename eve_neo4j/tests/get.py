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


class TestGetItem(TestBaseNeo4j):

    def assertItemResponse(self, response, status, resource=None):
        self.assert200(status)
        self.assertTrue(self.app.config['ETAG'] in response)
        links = response['_links']
        self.assertEqual(len(links), 3)
        self.assertHomeLink(links)
        self.assertCollectionLink(links, resource or self.known_resource)
        self.assertItem(response, resource or self.known_resource)

    def test_getitem_by_id(self):
        response, status = self.get(self.known_resource,
                                    item=self.item_id)
        self.assertItemResponse(response, status)

        response, status = self.get(self.known_resource,
                                    item=self.unknown_item_id)
        self.assert404(status)
