
from google.appengine.api.users import User as GAE_User

from ..importexport import load_items
from ..inventory import User, Currency, AccountingUniverse, Book


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


# ISO 4217 - http://en.wikipedia.org/wiki/ISO_4217
init_currencies = [
    Currency, [
        {'uid': 'XAU', 'name': 'Gold (one troy ounce)'},
        {'uid': 'XAG', 'name': 'Silver (one troy ounce)'},
        {'uid': 'USD', 'name': 'United States dollar'},
        {'uid': 'EUR', 'name': 'Euro'},
        {'uid': 'GBP', 'name': 'Pound sterling'},
        {'uid': 'JPY', 'name': 'Japanese yen'},
    ],
]

init_users = [
    User, [
        {'uid': 'alexamici', 'principal': GAE_User('alexamici@gmail.com'), 'default_currency': 'EUR', 'children': [
            Book, [
                {'uid': 'default', 'name': 'Default'}
            ],
        ]},
    ],
]

init_accounting_universes = [
    AccountingUniverse, [
        {'uid': 'GIFI', 'name': 'General Index of Financial Information',
            'description': 'GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf'},
    ],
]


def init_datastore():
    load_items(init_currencies)
    eur = Currency.get_by_key_name('EUR')
    load_items(init_accounting_universes)
    root = AccountingUniverse.get_by_key_name('GIFI')
    load_items(init_users, parent_key='owner', accounting_universe=root, currency=eur)
