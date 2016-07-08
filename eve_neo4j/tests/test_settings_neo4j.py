ID_FIELD = '_id'
ITEM_LOOKUP = True
ITEM_LOOKUP_FIELD = ID_FIELD

ALLOW_UNKNOWN = True

GRAPH_DATABASE = 'http://localhost:7474/db/data/'
GRAPH_USER = 'neo4j'
GRAPH_PASSWORD = 'admin'

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE', 'PUT']

people = {
    'item_title': 'person',
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'schema': {
        'invoices_collection': {
            'type': 'objectid',
            'data_relation': {
                'embeddable': True,
                'resource': 'invoices'
            }
        }
    }
}

invoices = {}

DOMAIN = {
    'people': people,
    'invoices': invoices
}
