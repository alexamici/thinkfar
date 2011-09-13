
from google.appengine.api.users import User as GAE_User

from ..importexport import load_items
from ..inventory import User, Currency, AccountingUniverse


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


# ISO 4217 - http://en.wikipedia.org/wiki/ISO_4217
init_currencies =(
    {'uid': 'XAU', 'name': 'Gold (one troy ounce)'},
    {'uid': 'XAG', 'name': 'Silver (one troy ounce)'},
    {'uid': 'USD', 'name': 'United States dollar'},
    {'uid': 'EUR', 'name': 'Euro'},
    {'uid': 'GBP', 'name': 'Pound sterling'},
    {'uid': 'JPY', 'name': 'Japanese yen'},
)

init_users = (
    {'uid': 'alexamici', 'principal': GAE_User('alexamici@gmail.com'), 'default_currency': 'EUR'},
)

init_accounting_universes = (
    {'uid': 'GIFI', 'name': 'General Index of Financial Information',
        'description': 'GIFI reference http://www.newlearner.com/courses/hts/bat4m/pdf/gifiguide.pdf'},
)


def init_datastore():
    load_items(Currency, init_currencies)
    load_items(User, init_users)
    load_items(AccountingUniverse, init_accounting_universes)
