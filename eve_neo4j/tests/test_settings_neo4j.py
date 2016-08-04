ID_FIELD = '_id'
ITEM_LOOKUP = True
ITEM_LOOKUP_FIELD = ID_FIELD
ITEM_URL = 'regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")'

GRAPH_DATABASE = 'http://graph:7474/db/data/'
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
        'invoices': {
            'type': 'relation',
            'datasource': {'source': 'has_invoice'},
            'schema': {
                'name': {
                    'type': 'string'
                },
                'prog': {
                    'type': 'number'
                }
            },
            'data_relation': {
                'embeddable': True,
                'resource': 'invoices'
            }
        },
        'prog': {
            'type': 'integer'
        },
        'firstname': {
            'type': 'string',
            'unique': True
        },
        'lastname': {
            'type': 'string'
        },
        'title': {
            'type': 'string',
            'default': 'Mr.'
        },
        'born': {
            'type': 'datetime',
            'required': False
        },
        'ref': {
            'type': 'string',
            'minlength': 25,
            'maxlength': 25,
        },
        'address': {
            'type': 'dict',
            'schema': {
                'address': {'type': 'string'},
                'city': {'type': 'string'}
            }
        }
    }
}

# flake8: noqa
import copy
users = copy.deepcopy(people)
users['url'] = 'users'
users['datasource'] = {'source': 'people',
                       'filter': 'prog < 5'}
users['resource_methods'] = ['DELETE', 'POST', 'GET']
users['item_title'] = 'user'

users_overseas = copy.deepcopy(users)
users_overseas['url'] = 'users/overseas'
users_overseas['datasource'] = {'source': 'people'}

invoices = {
    'schema': {
        'number': {
            'type': 'number'
        }
    }
}

user_invoices = copy.deepcopy(invoices)
user_invoices['url'] = 'users/<regex("[0-9]+"):people>/invoices'
user_invoices['datasource'] = {'source': 'invoices'}

payments = {
    'resource_methods': ['GET'],
    'item_methods': ['GET'],
}

DOMAIN = {
    'people': people,
    'users': users,
    'users_overseas': users_overseas,
    'invoices': invoices,
    'userinvoices': user_invoices,
    'payments': payments
}
